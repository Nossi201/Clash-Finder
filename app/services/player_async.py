# app/routes/player_async.py
"""
Asynchronous player routes for Clash Finder.
Loads page immediately and fetches matches via AJAX.
"""

import time
from flask import Blueprint, render_template, request, jsonify, current_app
from config.logging_config import get_logger, log_player_search, log_error_with_context
from app.utils.decorators import conditional_rate_limit, log_request_time
from app.utils.formatters import unslugify_server, decode_riot_id
from app.services.riot_api import (
    get_player_info,  # New function to get just player info
    display_matches,
    display_matches_by_value,
    servers_to_region
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
    Display player page immediately, matches load asynchronously.

    Args:
        riot_id: Encoded Riot ID (Name--TAG format)
        server: Server slug (e.g., 'eu-west')

    Returns:
        Rendered player history template (without matches, they load via AJAX)
    """
    start_time = time.time()

    # Decode parameters
    game_name, tag_line = decode_riot_id(riot_id)
    actual_server = unslugify_server(server)

    logger.info(f"Loading player page | Player: {game_name}#{tag_line} | Server: {actual_server}")

    try:
        # Just verify player exists (quick API call)
        # This could be a simple player info fetch if available
        # For now, we'll just pass the data to template

        player_data = {
            'summoner_name': game_name,
            'summoner_tag': tag_line,
            'server': actual_server,
            'server_slug': server,
            'riot_id': riot_id
        }

        logger.info(f"Player page loaded | Time: {time.time() - start_time:.2f}s")

        return render_template(
            'player_history_async.html',
            player_data=player_data,
            initial_load=True
        )

    except Exception as e:
        log_error_with_context(
            logger, e,
            f"Player: {game_name}#{tag_line}, Server: {actual_server}"
        )

        return render_template(
            'index.html',
            error_message=f"Error loading player: {str(e)}",
            servers=servers_to_region.keys()
        ), 500


@player_bp.route('/api/matches/<riot_id>/<server>')
@conditional_rate_limit(
    per_minute=30,
    per_hour=300
)
def get_matches(riot_id, server):
    """
    API endpoint to fetch matches asynchronously.

    Args:
        riot_id: Encoded Riot ID
        server: Server slug

    Query params:
        offset: Starting position (default 0)
        limit: Number of matches to fetch (default 5)

    Returns:
        JSON with matches data
    """
    start_time = time.time()

    # Get query parameters
    offset = request.args.get('offset', 0, type=int)
    limit = request.args.get('limit', 5, type=int)

    # Decode parameters
    game_name, tag_line = decode_riot_id(riot_id)
    actual_server = unslugify_server(server)

    logger.info(
        f"Fetching matches via API | Player: {game_name}#{tag_line} | "
        f"Offset: {offset} | Limit: {limit}"
    )

    try:
        # Fetch matches
        if offset == 0:
            # First load - get initial matches
            matches = display_matches(game_name, tag_line, actual_server, limit=limit)
        else:
            # Load more matches
            matches = display_matches_by_value(
                game_name, tag_line, actual_server, offset, limit
            )

        if not matches:
            logger.warning(f"No matches found | Offset: {offset}")
            return jsonify({
                'matches': [],
                'has_more': False,
                'total_loaded': offset
            })

        # Render match cards as HTML
        match_cards_html = []
        for match in matches:
            # Render each match card to HTML
            match_html = render_template(
                'components/match_card_async.html',
                match=match
            )
            match_cards_html.append(match_html)

        logger.info(
            f"Fetched {len(matches)} matches | Time: {time.time() - start_time:.2f}s"
        )

        return jsonify({
            'matches': match_cards_html,
            'has_more': len(matches) == limit,
            'total_loaded': offset + len(matches),
            'fetch_time': f"{time.time() - start_time:.2f}s"
        })

    except Exception as e:
        log_error_with_context(
            logger, e,
            f"API fetch for {game_name}#{tag_line}"
        )
        return jsonify({
            'error': str(e),
            'matches': [],
            'has_more': False
        }), 500


@player_bp.route('/api/player-info/<riot_id>/<server>')
@conditional_rate_limit(
    per_minute=30,
    per_hour=300
)
def get_player_info(riot_id, server):
    """
    Get basic player information (level, icon, etc).
    Quick API call for initial page load.

    Returns:
        JSON with player info
    """
    # Decode parameters
    game_name, tag_line = decode_riot_id(riot_id)
    actual_server = unslugify_server(server)

    try:
        # This would be a quick API call to get player info
        # For now, return basic data
        player_info = {
            'name': game_name,
            'tag': tag_line,
            'server': actual_server,
            'level': 'N/A',  # Would be fetched from API
            'icon': '/static/img/default-avatar.png'
        }

        return jsonify(player_info)

    except Exception as e:
        logger.error(f"Error fetching player info: {e}")
        return jsonify({'error': str(e)}), 500


# Backwards compatibility endpoint
@player_bp.route('/load_more', methods=['POST'])
@conditional_rate_limit(
    per_minute=20,
    per_hour=200
)
def load_more_matches():
    """
    Legacy endpoint for loading more matches.
    Redirects to new API endpoint.
    """
    data = request.get_json() or {}

    # Convert old format to new format
    game_name = data.get('SUMMONER_NAME', '')
    tag_line = data.get('SUMMONER_TAG', '')
    server = data.get('server', '')
    offset = data.get('current_count', 0)
    limit = data.get('number', 5)

    if not all([game_name, tag_line, server]):
        return jsonify({'error': 'Missing parameters'}), 400

    # Create riot_id
    riot_id = f"{game_name}--{tag_line}"

    # Call new API endpoint
    return get_matches(riot_id, server + f"?offset={offset}&limit={limit}")