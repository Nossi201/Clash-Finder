# app/routes/main.py
"""
Main routes for Clash Finder application.
Handles home page and search form submission.
"""

import time
from flask import Blueprint, render_template, request, redirect, url_for
from config.logging_config import get_logger
from app.utils.decorators import conditional_rate_limit, log_request_time
from app.utils.formatters import slugify_server, parse_summoner_input, encode_riot_id
from app.services.riot_api import servers_to_region

logger = get_logger('routes.main')

# Create blueprint
main_bp = Blueprint('main', __name__, url_prefix='')


@main_bp.route('/')
@conditional_rate_limit(
    per_minute=100,  # Config.RATE_LIMIT_HOME_MINUTE
    per_hour=1000  # Config.RATE_LIMIT_HOME_HOUR
)
def index():
    """
    Render the home page with server selection.

    Returns:
        Rendered template with available servers
    """
    logger.debug("Home page accessed")

    return render_template(
        'index.html',
        servers=servers_to_region.keys()
    )


@main_bp.route('/Cheker', methods=['POST'])
@conditional_rate_limit(
    per_minute=30,  # Config.RATE_LIMIT_SEARCH_MINUTE
    per_hour=300  # Config.RATE_LIMIT_SEARCH_HOUR
)
@log_request_time
def cheker():
    """
    Handle form submission for player search.
    Redirects to either player stats or clash team page.

    Form Fields:
        option: 'playerStats' or 'clashTeam'
        tekst: Summoner name (Riot ID with #tag)
        lista: Server name

    Returns:
        Redirect to appropriate endpoint
    """
    start_time = time.time()

    # Get form data
    option = request.form.get('option', 'playerStats')
    summoner_input = request.form.get('tekst', '').strip()
    server = request.form.get('lista', '').strip()

    # Validate inputs
    if not summoner_input:
        logger.warning("Empty summoner name submitted")
        return render_template(
            'index.html',
            error_message="Please enter a summoner name.",
            servers=servers_to_region.keys()
        ), 400

    if not server or server not in servers_to_region:
        logger.warning(f"Invalid server: {server}")
        return render_template(
            'index.html',
            error_message="Please select a valid server.",
            servers=servers_to_region.keys()
        ), 400

    # Parse Riot ID
    game_name, tag_line = parse_summoner_input(summoner_input)

    # Create URL-safe slugs
    riot_id_slug = encode_riot_id(game_name, tag_line)
    server_slug = slugify_server(server)

    logger.info(
        f"Search initiated | Name: {game_name}#{tag_line} | "
        f"Server: {server} | Option: {option}"
    )

    # Redirect based on option
    if option == 'clashTeam':
        logger.debug("Redirecting to clash team view")
        return redirect(url_for(
            'clash.clash_team',
            riot_id=riot_id_slug,
            server=server_slug
        ))

    # Default: player stats
    logger.debug(f"Redirecting to player stats | Time: {time.time() - start_time:.2f}s")
    return redirect(url_for(
        'player.player_stats',
        riot_id=riot_id_slug,
        server=server_slug
    ))


# Alternative route names for backwards compatibility
@main_bp.route('/home')
def home():
    """Alias for index route."""
    return redirect(url_for('main.index'))