# app.py
import ssl_env_config  # Import SSL configuration
from flask import Flask, render_template, request, redirect, url_for, jsonify

from config import FLASK_SECRET_KEY
from resource_manager import resource_manager, start_background_updater

from question import (
    get_account_info,
    get_summoner_info_puuid,
    get_team_info_puuid,
    get_tournament_id_by_team,
    show_players_team,
    servers_to_region, display_matches,
    display_matches_by_value
)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY
app.register_blueprint(resource_manager)
current_count = 20


def parse_summoner_name(summoner_name):
    """
    Parsuje nazwę gracza i zwraca tuple (name, tag)
    Obsługuje nowy format API gdzie nazwa i tag są osobno
    """
    if "#" in summoner_name:
        return summoner_name.split("#", 1)
    else:
        # Jeśli brak hashtagu, zwróć nazwę i pusty tag
        return summoner_name, ""


def slugify_server(server):
    """Konwertuje nazwę serwera na slug URL-friendly"""
    return server.lower().replace(' ', '-').replace('&', 'and')


def unslugify_server(slug):
    """Konwertuje slug z powrotem na nazwę serwera"""
    return slug.replace('-', ' ').replace('and', '&')


@app.route('/')
def home():
    return render_template('index.html', servers=servers_to_region.keys())


@app.route('/Cheker', methods=['POST'])
def clash_or_player():
    option = request.form.get('option')
    summoner_name = request.form.get('tekst')
    server = request.form.get('lista')

    if option == 'clashTeam':
        return redirect(url_for('clash_team',
                                summoner_name=summoner_name.replace('#', '--').replace(' ', '-'),
                                server=slugify_server(server)))
    elif option == 'playerStats':
        return redirect(url_for('player_stats',
                                summoner_name=summoner_name.replace('#', '--').replace(' ', '-'),
                                server=slugify_server(server)))
    else:
        return redirect(url_for('index'))


@app.route('/clash_team/<summoner_name>/<server>')
def clash_team(summoner_name, server):
    # Najpierw przywracamy #, potem spacje
    summoner_name = summoner_name.replace('--', '#').replace('-', ' ')
    server = unslugify_server(server)

    SUMMONER_NAME, SUMMONER_TAG = parse_summoner_name(summoner_name)
    SERVER = server
    try:
        account_info = get_account_info(SUMMONER_NAME, SUMMONER_TAG, SERVER)

        if not account_info:
            return render_template('index.html', error_message="Account information not found. Please, try again.",
                                   servers=servers_to_region.keys())
        puuid = account_info['puuid']
        summoner_info = get_summoner_info_puuid(puuid, SERVER)

        if not summoner_info:
            return render_template('index.html', error_message="Summoner information not found. Please, try again.",
                                   servers=servers_to_region.keys())

        summoner_id = summoner_info['id']
        teams_info = get_team_info_puuid(summoner_id, SERVER)

        if not teams_info:
            return render_template('index.html', error_message="Team information not found. Please, try again.",
                                   servers=servers_to_region.keys())

        all_players_info = []
        for team_info in teams_info:
            team_id = team_info['teamId']
            tournament_info = get_tournament_id_by_team(team_id, SERVER)

            if tournament_info:
                players = tournament_info['players']

                players_info = show_players_team(players, SERVER)
                all_players_info.extend(players_info)

        return render_template('clash_links.html', players_info=all_players_info)

    except Exception as e:
        return render_template('index.html', error_message="error: " + str(e), servers=servers_to_region.keys())


@app.route('/load_more_matches', methods=['POST'])
def load_more_matches():
    data = request.get_json()
    current_count = int(data.get('current_count', 0))
    number = int(data.get('number', 1))
    server = data.get('server', "")
    SUMMONER_NAME = data.get('SUMMONER_NAME', "")
    SUMMONER_TAG = data.get('SUMMONER_TAG', "")

    match_history_list_sorted = display_matches_by_value(SUMMONER_NAME, SUMMONER_TAG, server, current_count, number)
    return jsonify(match_history_list_sorted)


@app.route('/player_stats/<summoner_name>/<server>')
def player_stats(summoner_name, server):
    # Najpierw przywracamy #, potem spacje
    summoner_name = summoner_name.replace('--', '#').replace('-', ' ')
    server = unslugify_server(server)

    SUMMONER_NAME, SUMMONER_TAG = parse_summoner_name(summoner_name)
    try:
        match_history_list_sorted = display_matches(SUMMONER_NAME, SUMMONER_TAG, server)
        if not match_history_list_sorted:
            return render_template('index.html', error_message="Summoner information not found. Please, try again.",
                                   servers=servers_to_region.keys())
        return render_template('player_history.html', match_history_list_sorted=match_history_list_sorted)
    except Exception as e:
        return render_template('index.html', error_message="error: " + str(e), servers=servers_to_region.keys())


# Dodaj custom filter dla Jinja2
@app.template_filter('slugify_server')
def jinja_slugify_server(s):
    return slugify_server(s)


if __name__ == "__main__":
    start_background_updater()
    app.run(debug=True)