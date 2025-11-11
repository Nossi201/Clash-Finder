# app/routes/player.py
"""
Player routes for Clash Finder - MINIMAL ASYNC MODIFICATION.
Keeps original structure but loads first matches asynchronously.
"""

import time
from flask import Blueprint, render_template, request, jsonify, current_app

from config import DDRAGON_VERSION
from config.logging_config import get_logger, log_player_search, log_error_with_context
from app.utils.decorators import conditional_rate_limit, log_request_time
from app.utils.formatters import unslugify_server, decode_riot_id
from app.services.riot_api import (
    display_matches,
    display_matches_by_value,
    servers_to_region,
    get_account_info  # Just to verify player exists
)

logger = get_logger('routes.player')

# Create blueprint
player_bp = Blueprint('player', __name__, url_prefix='/player_stats')


@player_bp.route('/<riot_id>/<server>')
@conditional_rate_limit(
    per_minute=15,
    per_hour=150
)
@log_request_time
def player_stats(riot_id, server):
    """
    Display player page IMMEDIATELY, but with empty match list.
    JavaScript will load matches right after page loads.

    This is MINIMAL change - we just don't load matches here.
    """
    start_time = time.time()

    # Decode parameters
    game_name, tag_line = decode_riot_id(riot_id)
    actual_server = unslugify_server(server)

    logger.info(f"Loading player stats page | Player: {game_name}#{tag_line} | Server: {actual_server}")

    try:
        # Optional: Quick check if player exists (can be removed for even faster load)
        account_info = get_account_info(game_name, tag_line, actual_server)
        if not account_info:
            return render_template(
                'index.html',
                error_message="Player not found.",
                servers=servers_to_region.keys()
            )

        # CHANGE: Instead of loading matches, pass empty list
        # JavaScript will load them immediately after page renders
        logger.info(f"Page rendered (async mode) | Time: {time.time() - start_time:.2f}s")

        # Create a dummy first match just for player info
        dummy_match = {
            'summoner_name': game_name,
            'summoner_tag': tag_line,
            'SERVER': actual_server,
            'profileIconId': 0,  # Default icon
            'win': False  # Dummy value
        }

        return render_template(
            'player_history.html',
            match_history_list_sorted=[],  # Empty list - JS will fill it
            player_info=dummy_match,  # Pass player info separately
            async_mode=True  # Flag to enable async loading in template
        )

    except Exception as e:
        log_error_with_context(
            logger, e,
            f"Player: {game_name}#{tag_line}, Server: {actual_server}"
        )

        return render_template(
            'index.html',
            error_message=f"Error loading player data: {str(e)}",
            servers=servers_to_region.keys()
        ), 500


@player_bp.route('/load_initial', methods=['POST'])
@conditional_rate_limit(
    per_minute=30,
    per_hour=300
)
def load_initial_matches():
    """
    NEW ENDPOINT: Load initial matches via AJAX.
    Called immediately after page loads.
    """
    start_time = time.time()

    # Parse request data
    data = request.get_json() or {}
    server = data.get('server', '')
    game_name = data.get('SUMMONER_NAME', '')
    tag_line = data.get('SUMMONER_TAG', '')

    logger.info(f"Loading initial matches | Player: {game_name}#{tag_line}")

    if not all([server, game_name]):
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        # Load initial batch of matches
        matches = display_matches(game_name, tag_line, server)

        if not matches:
            logger.warning(f"No matches found for {game_name}#{tag_line}")
            return jsonify({'matches': [], 'total': 0})

        # Limit to first 10 for initial load
        initial_matches = matches[:10] if len(matches) > 10 else matches

        # Render match cards as HTML
        match_cards_html = []
        for match in initial_matches:
            match_html = render_template(
                'components/match_card.html',
                match=match,
                ddragon_version=DDRAGON_VERSION
            )
            match_cards_html.append(match_html)

        logger.info(f"Initial load complete | Matches: {len(initial_matches)} | Time: {time.time() - start_time:.2f}s")

        return jsonify({
            'matches': match_cards_html,
            'total': len(initial_matches),
            'has_more': len(matches) > 10
        })

    except Exception as e:
        logger.error(f"Error loading initial matches: {e}")
        return jsonify({'error': str(e)}), 500


@player_bp.route('/load_more', methods=['POST'])
@conditional_rate_limit(
    per_minute=20,
    per_hour=200
)
def load_more_matches(DDRAGON_VERSION='14.1.1'):
    """
    Load additional match entries.
    """
    from app.services.riot_api import process_raw_matches_for_player

    start_time = time.time()
    data = request.get_json() or {}
    current = data.get('current_count', 0)
    number = int(data.get('number', 1))
    server = data.get('server', '')
    game_name = data.get('SUMMONER_NAME', '')
    tag_line = data.get('SUMMONER_TAG', '')

    logger.debug(f"Load more matches | Player: {game_name}#{tag_line} | Current: {current} | Requesting: {number}")

    if not all([server, game_name]):
        logger.warning("Load more: Missing required parameters")
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        # Pobierz PUUID
        account_info = get_account_info(game_name, tag_line, server)
        if not account_info:
            return jsonify([]), 200

        puuid = account_info['puuid']

        # Fetch surowe dane
        raw_matches = display_matches_by_value(game_name, tag_line, server, current, number)

        if not raw_matches:
            logger.warning(f"No additional matches found | Player: {game_name}#{tag_line}")
            return jsonify([]), 200

        # Przetwórz używając helper function
        processed_matches = process_raw_matches_for_player(
            raw_matches,
            puuid,
            game_name,
            tag_line,
            server
        )

        # Renderuj HTML
        match_cards_html = []
        for match in processed_matches:
            match_html = render_template('components/match_card.html', match=match, ddragon_version=DDRAGON_VERSION)
            match_cards_html.append(match_html)

        logger.info(f"Loaded {len(match_cards_html)} additional matches | Time: {time.time() - start_time:.2f}s")

        return jsonify(match_cards_html)

    except Exception as e:
        log_error_with_context(logger, e, f"Load more for {game_name}#{tag_line}")
        return jsonify({'error': str(e)}), 500


@player_bp.route('/load_batch', methods=['POST'])
@conditional_rate_limit(
    per_minute=50,
    per_hour=500
)
def load_batch():
    """
    Load a small batch of matches (progressive loading).
    Uses the SAME logic as load_initial for consistency.
    """
    start_time = time.time()

    data = request.get_json() or {}
    server = data.get('server', '')
    game_name = data.get('SUMMONER_NAME', '')
    tag_line = data.get('SUMMONER_TAG', '')
    offset = int(data.get('offset', 0))
    batch_size = int(data.get('batch_size', 2))

    logger.debug(f"Loading batch | Player: {game_name}#{tag_line} | Offset: {offset} | Size: {batch_size}")

    if not all([server, game_name]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        # Używamy tej samej funkcji co load_initial - display_matches()
        # Cache sprawi że będzie szybko
        all_matches = display_matches(game_name, tag_line, server)

        if not all_matches:
            logger.warning(f"No matches found for player")
            return jsonify({'matches': [], 'has_more': False, 'offset': offset})

        # Wytnij tylko potrzebny fragment (slice)
        end_offset = offset + batch_size
        batch_matches = all_matches[offset:end_offset]

        if not batch_matches:
            logger.warning(f"No matches in range {offset}:{end_offset}")
            return jsonify({'matches': [], 'has_more': False, 'offset': offset})

        # Render match cards - IDENTYCZNIE JAK W load_initial
        match_cards_html = []
        for match in batch_matches:
            match_html = render_template(
                'components/match_card.html',
                match=match,
                ddragon_version=DDRAGON_VERSION
            )
            match_cards_html.append(match_html)

        logger.info(
            f"Batch loaded | Matches: {len(match_cards_html)}/{len(all_matches)} | "
            f"Offset: {offset} | Time: {time.time() - start_time:.2f}s"
        )

        return jsonify({
            'matches': match_cards_html,
            'total_loaded': len(match_cards_html),
            'offset': offset + len(match_cards_html),
            'has_more': (offset + len(match_cards_html)) < len(all_matches)
        })

    except Exception as e:
        logger.error(f"Error loading batch: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

# Alternative route for backwards compatibility
@player_bp.route('/', methods=['POST'])
def load_more_matches_alt():
    """Alternative endpoint for load more (backwards compatibility)."""
    return load_more_matches()


@player_bp.route('/load_more_simple', methods=['GET'])
def load_more_simple():
    try:
        from app.services.riot_api import process_raw_matches_for_player

        # Użyj 'start' jako offset w liście meczów
        start = int(request.args.get('start', 0))
        count = int(request.args.get('count', 5))
        game_name = request.args.get('name', '')
        tag_line = request.args.get('tag', '')
        server = request.args.get('server', '')

        logger.debug(f"load_more_simple | start={start} | count={count} | player={game_name}#{tag_line}")

        if not server or not game_name:
            return jsonify({'items': [], 'hasMore': False}), 400

        # Pobierz account info żeby mieć PUUID
        account_info = get_account_info(game_name, tag_line, server)
        if not account_info:
            return jsonify({'items': [], 'hasMore': False}), 400

        puuid = account_info['puuid']

        # Pobierz surowe dane meczów używając display_matches_by_value
        raw_matches = display_matches_by_value(game_name, tag_line, server, start, count)

        if not raw_matches:
            logger.info(f"No more matches available from offset {start}")
            return jsonify({'items': [], 'hasMore': False})

        # Przetwórz surowe dane używając helper function
        processed_matches = process_raw_matches_for_player(
            raw_matches,
            puuid,
            game_name,
            tag_line,
            server
        )

        if not processed_matches:
            logger.info(f"No matches after processing")
            return jsonify({'items': [], 'hasMore': False})

        # Renderuj karty jako HTML
        items = []
        for match in processed_matches:
            html = render_template('components/match_card.html', match=match, ddragon_version=DDRAGON_VERSION)
            items.append(html)

        # Jeśli otrzymaliśmy mniej niż count, to nie ma więcej
        has_more = len(raw_matches) == count

        logger.info(f"load_more_simple complete | loaded={len(items)} | hasMore={has_more}")

        return jsonify({'items': items, 'hasMore': has_more})
    except Exception as e:
        logger.error(f"load_more_simple error: {e}", exc_info=True)
        return jsonify({'items': [], 'hasMore': False}), 500