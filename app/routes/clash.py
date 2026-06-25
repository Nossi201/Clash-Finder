# app/routes/clash.py
"""
Clash team routes for Clash Finder.
Handles clash team information and player lookups.
"""

import time
from flask import Blueprint, render_template, current_app
from config.logging_config import get_logger, log_error_with_context
from app.utils.decorators import conditional_rate_limit, log_request_time
from app.utils.formatters import unslugify_server, decode_riot_id
from app.services.riot_api import (
    get_account_info,
    get_summoner_info_puuid,
    get_team_info_puuid,
    get_tournament_id_by_team,
    show_players_team,
    servers_to_region
)

logger = get_logger('routes.clash')

# Create blueprint
clash_bp = Blueprint('clash', __name__, url_prefix='/clash_team')


@clash_bp.route('/<riot_id>/<server>')
@conditional_rate_limit(
    per_minute=15,  # Config.RATE_LIMIT_CLASH_TEAM_MINUTE
    per_hour=150  # Config.RATE_LIMIT_CLASH_TEAM_HOUR
)
@log_request_time
def clash_team(riot_id, server):
    """
    Display clash team information for the given summoner.

    Args:
        riot_id: Encoded Riot ID (Name--TAG format)
        server: Server slug (e.g., 'eu-west')

    Returns:
        Rendered clash team template or error page
    """
    start_time = time.time()

    # Decode parameters
    game_name, tag_line = decode_riot_id(riot_id)
    actual_server = unslugify_server(server)

    logger.info(f"Loading clash team | Player: {game_name}#{tag_line} | Server: {actual_server}")

    try:
        # Step 1: Get account info by Riot ID
        account_info = get_account_info(game_name, tag_line, actual_server)

        if not account_info:
            logger.warning(f"Account not found for clash team | Player: {game_name}#{tag_line}")
            return render_template(
                'index.html',
                error_message="Account not found. Please check the summoner name and tag.",
                servers=servers_to_region.keys()
            ), 404

        # Step 2: Get summoner info using PUUID
        puuid = account_info['puuid']
        summoner_info = get_summoner_info_puuid(puuid, actual_server)

        if not summoner_info:
            logger.warning(f"Summoner not found for clash team | PUUID: {puuid[:8]}...")
            return render_template(
                'index.html',
                error_message="Summoner information not found.",
                servers=servers_to_region.keys()
            ), 404

        # Step 3: Get team info using summoner ID
        team_info = get_team_info_puuid(summoner_info['id'], actual_server)

        if not team_info:
            logger.info(f"No clash team found | Player: {game_name}#{tag_line}")
            return render_template(
                'index.html',
                error_message="This player is not currently in a clash team.",
                servers=servers_to_region.keys()
            ), 404

        # Step 4: Get tournament ID and team players
        tournament_id = get_tournament_id_by_team(team_info)

        if not tournament_id:
            logger.warning(f"No tournament ID found | Player: {game_name}#{tag_line}")
            return render_template(
                'index.html',
                error_message="Unable to retrieve clash team information.",
                servers=servers_to_region.keys()
            ), 404

        # Step 5: Get all players in the team
        players = show_players_team(tournament_id)

        if not players:
            logger.warning(f"No players found in clash team | Tournament: {tournament_id}")
            return render_template(
                'index.html',
                error_message="No players found in the clash team.",
                servers=servers_to_region.keys()
            ), 404

        # Success
        logger.info(
            f"Clash team loaded | Players: {len(players)} | "
            f"Time: {time.time() - start_time:.2f}s"
        )

        return render_template(
            'clash_team.html',
            players_team=players
        )

    except KeyError as e:
        log_error_with_context(
            logger, e,
            f"Missing key in clash team data for {game_name}#{tag_line}, {actual_server}"
        )
        return render_template(
            'index.html',
            error_message="Error: Invalid data structure from API.",
            servers=servers_to_region.keys()
        ), 500

    except Exception as e:
        log_error_with_context(
            logger, e,
            f"Clash team for {game_name}#{tag_line}, {actual_server}"
        )
        return render_template(
            'index.html',
            error_message="Unable to load clash team data. Please try again.",
            servers=servers_to_region.keys()
        ), 500