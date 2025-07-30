# app.py
import ssl_env_config
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify

from config import FLASK_SECRET_KEY
from resource_manager import resource_manager, start_background_updater
from question import (
    parse_summoner_name,
    get_account_info,
    get_summoner_info_puuid,
    get_team_info_puuid,
    get_tournament_id_by_team,
    show_players_team,
    servers_to_region,
    display_matches,
    display_matches_by_value
)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.register_blueprint(resource_manager)


def slugify_server(server):
    """Convert a server name into a URL-friendly slug."""
    return server.lower().replace(' ', '-').replace('&', 'and')


def unslugify_server(slug):
    """Convert a URL slug back into a server name."""
    result = slug.replace('-', ' ')
    result = re.sub(r'\band\b', '&', result)
    return result


@app.route('/')
def home():
    """Render the home page with the list of available servers."""
    return render_template('index.html', servers=servers_to_region.keys())


@app.route('/Cheker', methods=['POST'])
def clash_or_player():
    """Handle form submission to navigate to clash team or player stats."""
    option = request.form.get('option')
    summoner_name = request.form.get('tekst')
    server = request.form.get('lista')

    slug_name = summoner_name.replace('#', '--').replace(' ', '-')
    slug_server = slugify_server(server)

    if option == 'clashTeam':
        return redirect(url_for('clash_team', summoner_name=slug_name, server=slug_server))
    return redirect(url_for('player_stats', summoner_name=slug_name, server=slug_server))


@app.route('/clash_team/<summoner_name>/<server>')
def clash_team(summoner_name, server):
    """Display clash team information for the given summoner."""
    actual_name = summoner_name.replace('--', '#').replace('-', ' ')
    actual_server = unslugify_server(server)
    base, tag = parse_summoner_name(actual_name)

    try:
        account_info = get_account_info(base, tag, actual_server)
        if not account_info:
            return render_template('index.html', error_message="Account not found.", servers=servers_to_region.keys())
        puuid = account_info['puuid']
        summoner_info = get_summoner_info_puuid(puuid, actual_server)
        if not summoner_info:
            return render_template('index.html', error_message="Summoner not found.", servers=servers_to_region.keys())
        team_info = get_team_info_puuid(summoner_info['id'], actual_server)
        tournament_id = get_tournament_id_by_team(team_info)
        players = show_players_team(tournament_id)
        return render_template('clash_team.html', players_team=players)
    except Exception as e:
        return render_template('index.html', error_message=f"Error: {e}", servers=servers_to_region.keys())


@app.route('/load_more_matches', methods=['POST'])
def load_more_matches():
    """Load additional match entries asynchronously."""
    data = request.get_json() or {}
    current = data.get('current_count', 0)
    number = int(data.get('number', 1))
    server = data.get('server', '')
    base = data.get('SUMMONER_NAME', '')
    tag = data.get('SUMMONER_TAG', '')

    new_matches = display_matches_by_value(base, tag, server, current, number)
    return jsonify(new_matches)


@app.route('/player_stats/<summoner_name>/<server>')
def player_stats(summoner_name, server):
    """Display player match history and detailed stats."""
    actual_name = summoner_name.replace('--', '#').replace('-', ' ')
    actual_server = unslugify_server(server)
    base, tag = parse_summoner_name(actual_name)

    try:
        matches = display_matches(base, tag, actual_server)
        if not matches:
            return render_template('index.html', error_message="Player not found.", servers=servers_to_region.keys())
        return render_template('player_history.html', match_history_list_sorted=matches)
    except Exception as e:
        return render_template('index.html', error_message=f"Error: {e}", servers=servers_to_region.keys())


@app.template_filter('slugify_server')
def jinja_slugify_server(s):
    """Jinja filter to slugify server names in templates."""
    return slugify_server(s)


if __name__ == "__main__":
    """Start the background updater and run the Flask application."""
    start_background_updater()
    app.run(debug=True)
