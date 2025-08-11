# app.py
import ssl_env_config
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify

from config import FLASK_SECRET_KEY
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

# Import CDN helper functions
from cdn_config import (
    get_image_url,
    get_champion_image_url,
    get_item_image_url,
    get_rune_image_url,
    get_rune_style_image_url,
    get_summoner_spell_image_url,
    get_stat_shard_image_url,
    get_item_name,
    get_rune_name,
    get_rune_style_name,
    get_summoner_spell_name,
    get_stat_shard_name,
    riot_cdn,
)

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# Register CDN helper functions for Jinja2 templates
app.jinja_env.globals.update(
    # image URLs
    get_image_url=get_image_url,
    get_champion_image_url=get_champion_image_url,
    get_item_image_url=get_item_image_url,
    get_rune_image_url=get_rune_image_url,
    get_rune_style_image_url=get_rune_style_image_url,
    get_summoner_spell_image_url=get_summoner_spell_image_url,
    get_stat_shard_image_url=get_stat_shard_image_url,
    # localized names
    get_item_name=get_item_name,
    get_rune_name=get_rune_name,
    get_rune_style_name=get_rune_style_name,
    get_summoner_spell_name=get_summoner_spell_name,
    get_stat_shard_name=get_stat_shard_name,
)


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


@app.route('/debug/check-static')
def debug_check_static():
    """Debug endpoint to check static files"""
    import os
    static_folder = app.static_folder
    js_path = os.path.join(static_folder, 'js', 'player_history.js')

    return {
        'static_folder': static_folder,
        'js_file_exists': os.path.exists(js_path),
        'js_path': js_path,
        'static_url_path': app.static_url_path,
        'files_in_static': os.listdir(static_folder) if os.path.exists(static_folder) else [],
        'files_in_js': os.listdir(os.path.join(static_folder, 'js')) if os.path.exists(
            os.path.join(static_folder, 'js')) else []
    }


@app.route('/debug/test-load-more')
def debug_test_load_more():
    """Debug endpoint to test load more functionality"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Test Load More</title>
        <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    </head>
    <body>
        <h1>Test Load More Functionality</h1>
        <button id="testButton">Test Load More Request</button>
        <div id="result"></div>

        <script>
        document.getElementById('testButton').addEventListener('click', async function() {
            const testData = {
                current_count: 20,
                number: 10,
                server: "eu west",
                SUMMONER_NAME: "HextechChest",
                SUMMONER_TAG: "202"
            };

            try {
                const response = await fetch('/load_more_matches', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(testData)
                });

                const result = await response.json();
                document.getElementById('result').innerHTML = 
                    '<pre>' + JSON.stringify(result, null, 2) + '</pre>';
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    '<p style="color: red;">Error: ' + error.message + '</p>';
            }
        });
        </script>
    </body>
    </html>
    """


@app.route('/load_more_matches', methods=['POST'])
def load_more_matches():
    """Load additional match entries asynchronously."""
    data = request.get_json() or {}
    current = data.get('current_count', 0)
    number = int(data.get('number', 1))
    server = data.get('server', '')
    base = data.get('SUMMONER_NAME', '')
    tag = data.get('SUMMONER_TAG', '')

    try:
        new_matches = display_matches_by_value(base, tag, server, current, number)

        if new_matches is None:
            return jsonify({'error': 'No matches found'}), 404

        # Add server info to first match for JavaScript processing
        if new_matches and len(new_matches) > 0:
            if len(new_matches[0]) > 0:
                new_matches[0][0]['SERVER'] = server
                new_matches[0][0]['summoner_name'] = base
                new_matches[0][0]['summoner_tag'] = tag

        return jsonify(new_matches)

    except Exception as e:
        print(f"Error in load_more_matches: {e}")
        return jsonify({'error': str(e)}), 500


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


# CDN Debug endpoints (tylko dla developmentu)
@app.route('/api/cdn/test')
def cdn_test():
    """Test endpoint to verify CDN functionality"""
    try:
        version = riot_cdn.get_current_version()
        champion_url = riot_cdn.get_champion_url("Aatrox")
        item_url = riot_cdn.get_item_url(1001)

        return jsonify({
            'status': 'success',
            'version': version,
            'sample_urls': {
                'champion': champion_url,
                'item': item_url
            }
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == "__main__":
    """Start the Flask application."""
    app.run(debug=True)