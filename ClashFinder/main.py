import requests

# Stałe
API_KEY = "RGAPI-87c65200-5671-493e-a557-aee6dd9d6103"
HEADERS = {"X-Riot-Token": API_KEY}
servers_to_region = {
    'brazil': ['br1', 'americas', 'br'],
    'latin america north': ['la1', 'americas', 'lan'],
    'latin america south': ['la2', 'americas', 'las'],
    'north america': ['na1', 'americas', 'na'],
    'japan': ['jp1', 'asia', 'jp'],
    'korea': ['kr', 'asia', 'kr'],
    'philippines': ['ph2', 'asia', 'ph'],
    'singapore': ['sg2', 'asia', 'sg'],
    'thailand': ['th2', 'asia', 'th'],
    'taiwan': ['tw2', 'asia', 'tw'],
    'vietnam': ['vn2', 'asia', 'vn'],
    'eu nordic & east': ['eun1', 'europe', 'eune'],
    'eu west': ['euw1', 'europe', 'euw'],
    'russia': ['ru', 'europe', 'ru'],
    'turkey': ['tr1', 'europe', 'tr']
}


def send_get_request(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Nie udało się uzyskać informacji. URL: {url}, Status Code: {response.status_code}")
        return None


def get_account_info(summoner_name, summoner_tag, SERVER):
    url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}"
    return send_get_request(url)


def get_summoner_info_puuid(puuid, SERVER):
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    return send_get_request(url)


def get_team_info_puuid(summoner_id, SERVER):
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/clash/v1/players/by-summoner/{summoner_id}"
    return send_get_request(url)


def get_tournament_id_by_team(team_id, SERVER):
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/clash/v1/teams/{team_id}"
    return send_get_request(url)


def show_players_team(players, SERVER):
    players_info = []
    for player in players:
        player_info = []
        league_entries_url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/league/v4/entries/by-summoner/{player['summonerId']}"
        summoner_entries = send_get_request(league_entries_url)

        if summoner_entries:
            player_info.extend([entry['queueType'] for entry in summoner_entries])  # Przykład rozszerzenia danych gracza

        if player_info:  # Dodajemy tylko, jeśli udało się uzyskać informacje
            players_info.append(player_info)
    return players_info


if __name__ == "__main__":
    SUMMONER_NAME = "Nossi"
    SUMMONER_TAG = "201"
    SERVER = "eu nordic & east"
    get_account_info(SUMMONER_NAME, SUMMONER_TAG)
