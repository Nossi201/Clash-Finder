#app.py
from flask import Flask, render_template, request
from question import (
    get_account_info,
    get_summoner_info_puuid,
    get_team_info_puuid,
    get_tournament_id_by_team,
    show_players_team,
    servers_to_region
)

app = Flask(__name__)


@app.route('/')
def home():
    # Przekazuje klucze servers_to_region do szablonu
    return render_template('index.html', servers=servers_to_region.keys())


@app.route('/tutaj_endpoint', methods=['POST'])
def handle_form():
    tekst = request.form['tekst']
    SUMMONER_NAME, SUMMONER_TAG = tekst.split("#") if "#" in tekst else (tekst, "")
    SERVER = request.form['lista']
    account_info = get_account_info(SUMMONER_NAME, SUMMONER_TAG, SERVER)

    if not account_info:
        return render_template('error.html', message="Nie znaleziono informacji o koncie.")

    puuid = account_info['puuid']
    summoner_info = get_summoner_info_puuid(puuid, SERVER)

    if not summoner_info:
        return render_template('error.html', message="Nie znaleziono informacji o przywoływaczu.")

    summoner_id = summoner_info['id']
    teams_info = get_team_info_puuid(summoner_id, SERVER)

    if not teams_info:
        return render_template('error.html', message="Nie znaleziono informacji o drużynach.")

    # Przykład wykorzystania danych z teams_info w Twojej aplikacji
    # Tutaj możesz iterować przez teams_info, uzyskać szczegóły drużyn i graczy itp.
    # Poniższy przykład zakłada, że chcesz wyświetlić informacje o drużynach graczy:
    all_players_info = []
    for team_info in teams_info:
        team_id = team_info['teamId']
        tournament_info = get_tournament_id_by_team(team_id, SERVER)
        if tournament_info:
            players = tournament_info['players']
            players_info = show_players_team(players, SERVER)
            all_players_info.extend(players_info)

    return render_template('players_info.html', players_info=all_players_info)


if __name__ == "__main__":
    app.run(debug=True)
