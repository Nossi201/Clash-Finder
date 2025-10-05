# app/routes/player.py
"""
Player routes for Clash Finder.
Handles player stats, match history, and load more functionality.
"""

import time
from flask import Blueprint, render_template, request, jsonify, current_app
from config.logging_config import get_logger, log_player_search, log_error_with_context
from app.utils.decorators import conditional_rate_limit, log_request_time
from app.utils.formatters import unslugify_server, decode_riot_id
from app.services.riot_api import (
    display_matches,
    display_matches_by_value,
    servers_to_region
)

logger = get_logger('routes.player')

# Create blueprint
player_bp = Blueprint('player', __name__, url_prefix='/player_stats')


@player_bp.route('/<riot_id>/<server>')
@conditional_rate_limit(
    per_minute=15,  # Config.RATE_LIMIT_PLAYER_STATS_MINUTE
    per_hour=150  # Config.RATE_LIMIT_PLAYER_STATS_HOUR
)
@log_request_time
def player_stats(riot_id, server):
    """
    Display player match history and detailed stats.

    Args:
        riot_id: Encoded Riot ID (Name--TAG format)
        server: Server slug (e.g., 'eu-west')

    Returns:
        Rendered player history template or error page
    """
    start_time = time.time()

    # Decode parameters
    game_name, tag_line = decode_riot_id(riot_id)
    actual_server = unslugify_server(server)

    logger.info(f"Loading player stats | Player: {game_name}#{tag_line} | Server: {actual_server}")

    try:
        # Fetch match history
        matches = display_matches(game_name, tag_line, actual_server)

        if not matches:
            log_player_search(logger, f"{game_name}#{tag_line}", actual_server, found=False)
            logger.warning(f"No matches found for {game_name}#{tag_line} on {actual_server}")

            return render_template(
                'index.html',
                error_message="Player not found or has no recent matches.",
                servers=servers_to_region.keys()
            )

        # Success
        log_player_search(logger, f"{game_name}#{tag_line}", actual_server, found=True)
        logger.info(
            f"Successfully loaded {len(matches)} matches | "
            f"Time: {time.time() - start_time:.2f}s"
        )

        return render_template(
            'player_history.html',
            match_history_list_sorted=matches
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


@player_bp.route('/load_more', methods=['POST'])
@conditional_rate_limit(
    per_minute=20,  # Config.RATE_LIMIT_LOAD_MORE_MINUTE
    per_hour=200  # Config.RATE_LIMIT_LOAD_MORE_HOUR
)
def load_more_matches():
    """
    Load additional match entries asynchronously.

    Expects JSON:
        {
            "current_count": int,
            "number": int,
            "server": str,
            "SUMMONER_NAME": str,
            "SUMMONER_TAG": str
        }

    Returns:
        JSON with additional matches or error
    """
    start_time = time.time()

    # Parse request data
    data = request.get_json() or {}
    current = data.get('current_count', 0)
    number = int(data.get('number', 1))
    server = data.get('server', '')
    game_name = data.get('SUMMONER_NAME', '')
    tag_line = data.get('SUMMONER_TAG', '')

    logger.debug(
        f"Load more matches | Player: {game_name}#{tag_line} | "
        f"Current: {current} | Requesting: {number}"
    )

    # Validate inputs
    if not all([server, game_name]):
        logger.warning("Load more: Missing required parameters")
        return jsonify({'error': 'Missing required parameters'}), 400

    try:
        # Fetch additional matches
        new_matches = display_matches_by_value(
            game_name, tag_line, server, current, number
        )

        if new_matches is None or not new_matches:
            logger.warning(f"No additional matches found | Player: {game_name}#{tag_line}")
            return jsonify({'error': 'No more matches found'}), 404

        # Add server info to first match for JavaScript processing
        if new_matches and len(new_matches) > 0:
            if len(new_matches[0]) > 0:
                new_matches[0][0]['SERVER'] = server
                new_matches[0][0]['summoner_name'] = game_name
                new_matches[0][0]['summoner_tag'] = tag_line

        logger.info(
            f"Loaded {len(new_matches)} additional matches | "
            f"Time: {time.time() - start_time:.2f}s"
        )

        return jsonify(new_matches)

    except Exception as e:
        log_error_with_context(logger, e, f"Load more for {game_name}#{tag_line}")
        return jsonify({'error': str(e)}), 500


# Alternative route for backwards compatibility
@player_bp.route('/', methods=['POST'])
def load_more_matches_alt():
    """Alternative endpoint for load more (backwards compatibility)."""
    return load_more_matches()