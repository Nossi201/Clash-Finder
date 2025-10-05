# app/template_filters.py
"""
Custom Jinja2 template filters for Clash Finder.
"""

from datetime import datetime
from flask import Flask

from app.utils.formatters import (
    format_game_duration,
    format_kda,
    calculate_kda_ratio,
    format_gold,
    format_damage,
    format_percentage,
    format_number
)
from config.game_constants import (
    get_queue_name,
    get_game_mode_name,
    get_summoner_spell_name,
    get_position_name
)


def register_template_filters(app: Flask):
    """
    Register custom Jinja2 filters.

    Args:
        app: Flask application instance
    """

    @app.template_filter('timestamp_to_date')
    def timestamp_to_date_filter(timestamp):
        """Convert timestamp to date string."""
        try:
            if timestamp:
                dt = datetime.fromtimestamp(timestamp / 1000)
                return dt.strftime('%d.%m.%Y %H:%M')
            return 'N/A'
        except (ValueError, TypeError, OverflowError):
            return 'N/A'

    @app.template_filter('spell_icon')
    def spell_icon_filter(spell_id):
        """Get spell icon name from ID."""
        # Mapping of common spell IDs to icon names
        spell_icons = {
            1: 'SummonerBoost',
            3: 'SummonerExhaust',
            4: 'SummonerFlash',
            6: 'SummonerHaste',
            7: 'SummonerHeal',
            11: 'SummonerSmite',
            12: 'SummonerTeleport',
            13: 'SummonerMana',
            14: 'SummonerDot',
            21: 'SummonerBarrier',
            30: 'SummonerPoroRecall',
            31: 'SummonerPoroThrow',
            32: 'SummonerSnowball',
        }
        return spell_icons.get(spell_id, 'SummonerBlank')

    @app.template_filter('time_ago')
    def time_ago_filter(timestamp):
        """Convert timestamp to 'time ago' format."""
        try:
            if not timestamp:
                return 'N/A'

            dt = datetime.fromtimestamp(timestamp / 1000)
            now = datetime.now()
            diff = now - dt

            seconds = diff.total_seconds()

            if seconds < 60:
                return 'przed chwilą'
            elif seconds < 3600:
                minutes = int(seconds / 60)
                return f'{minutes} min temu'
            elif seconds < 86400:
                hours = int(seconds / 3600)
                return f'{hours} godz. temu'
            elif seconds < 604800:
                days = int(seconds / 86400)
                return f'{days} dni temu'
            elif seconds < 2592000:
                weeks = int(seconds / 604800)
                return f'{weeks} tyg. temu'
            else:
                return dt.strftime('%d.%m.%Y')
        except (ValueError, TypeError, OverflowError):
            return 'N/A'

    @app.template_filter('champion_icon')
    def champion_icon_filter(champion_name, version='14.1.1'):
        """Get champion icon URL."""
        return f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_name}.png"

    @app.template_filter('kda_color')
    def kda_color_filter(kda):
        """Get color class based on KDA ratio."""
        try:
            kda_value = float(kda)
            if kda_value >= 5:
                return 'kda-excellent'
            elif kda_value >= 3:
                return 'kda-good'
            elif kda_value >= 2:
                return 'kda-average'
            else:
                return 'kda-poor'
        except (ValueError, TypeError):
            return 'kda-average'

    @app.template_filter('win_rate')
    def win_rate_filter(wins, total):
        """Calculate win rate percentage."""
        try:
            if total == 0:
                return '0%'
            percentage = (wins / total) * 100
            return f"{percentage:.1f}%"
        except (ValueError, TypeError, ZeroDivisionError):
            return '0%'

    @app.template_filter('shorten')
    def shorten_filter(text, length=50):
        """Shorten text to specified length."""
        if not text:
            return ''
        if len(text) <= length:
            return text
        return text[:length] + '...'

    # Register formatting filters
    app.jinja_env.filters['format_duration'] = format_game_duration
    app.jinja_env.filters['format_kda'] = format_kda
    app.jinja_env.filters['calc_kda'] = calculate_kda_ratio
    app.jinja_env.filters['format_gold'] = format_gold
    app.jinja_env.filters['format_damage'] = format_damage
    app.jinja_env.filters['format_percentage'] = format_percentage
    app.jinja_env.filters['format_number'] = format_number

    # Register game constant filters
    app.jinja_env.filters['queue_name'] = get_queue_name
    app.jinja_env.filters['game_mode_name'] = get_game_mode_name
    app.jinja_env.filters['spell_name'] = get_summoner_spell_name
    app.jinja_env.filters['position_name'] = get_position_name