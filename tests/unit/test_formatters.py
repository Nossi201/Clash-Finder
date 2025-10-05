# tests/unit/test_formatters.py
"""
Unit tests for formatting utilities.
"""

import pytest
from app.utils.formatters import (
    slugify_server,
    unslugify_server,
    encode_riot_id,
    decode_riot_id,
    parse_summoner_input,
    format_game_duration,
    format_kda,
    calculate_kda_ratio,
    format_cs,
    calculate_cs_per_min,
    format_gold,
    format_damage,
    sanitize_filename,
    truncate_text,
    format_percentage,
    format_number
)


class TestServerFormatting:
    """Test server name formatting."""

    def test_slugify_server_euw(self):
        assert slugify_server('EUW') == 'eu-west'

    def test_slugify_server_na(self):
        assert slugify_server('NA') == 'north-america'

    def test_slugify_server_lowercase(self):
        assert slugify_server('euw') == 'eu-west'

    def test_slugify_server_unknown(self):
        result = slugify_server('UNKNOWN')
        assert result == 'unknown'

    def test_unslugify_server_euw(self):
        assert unslugify_server('eu-west') == 'EUW'

    def test_unslugify_server_na(self):
        assert unslugify_server('north-america') == 'NA'

    def test_unslugify_server_unknown(self):
        result = unslugify_server('unknown-server')
        assert result == 'UNKNOWN-SERVER'

    def test_roundtrip_conversion(self):
        original = 'EUW'
        slug = slugify_server(original)
        back = unslugify_server(slug)
        assert back == original


class TestRiotIDFormatting:
    """Test Riot ID encoding/decoding."""

    def test_encode_riot_id_simple(self):
        result = encode_riot_id('Player', 'TAG')
        assert result == 'Player--TAG'

    def test_encode_riot_id_with_spaces(self):
        result = encode_riot_id('Player Name', 'TAG')
        assert 'Player' in result
        assert 'TAG' in result
        assert '--' in result

    def test_encode_riot_id_special_chars(self):
        result = encode_riot_id('Player#123', 'TAG')
        assert '--' in result

    def test_decode_riot_id_simple(self):
        game_name, tag_line = decode_riot_id('Player--TAG')
        assert game_name == 'Player'
        assert tag_line == 'TAG'

    def test_decode_riot_id_with_encoding(self):
        encoded = encode_riot_id('Player Name', 'TAG')
        game_name, tag_line = decode_riot_id(encoded)
        assert game_name == 'Player Name'
        assert tag_line == 'TAG'

    def test_decode_riot_id_invalid_format(self):
        game_name, tag_line = decode_riot_id('InvalidFormat')
        assert game_name == 'InvalidFormat'
        assert tag_line == ''

    def test_roundtrip_riot_id(self):
        original_name = 'TestPlayer'
        original_tag = 'EUW1'
        encoded = encode_riot_id(original_name, original_tag)
        decoded_name, decoded_tag = decode_riot_id(encoded)
        assert decoded_name == original_name
        assert decoded_tag == original_tag


class TestSummonerInputParsing:
    """Test summoner input parsing."""

    def test_parse_with_tag(self):
        game_name, tag_line = parse_summoner_input('Player#TAG')
        assert game_name == 'Player'
        assert tag_line == 'TAG'

    def test_parse_without_tag(self):
        game_name, tag_line = parse_summoner_input('Player')
        assert game_name == 'Player'
        assert tag_line == ''

    def test_parse_with_spaces(self):
        game_name, tag_line = parse_summoner_input('  Player Name  #  TAG  ')
        assert game_name == 'Player Name'
        assert tag_line == 'TAG'

    def test_parse_multiple_hash(self):
        game_name, tag_line = parse_summoner_input('Player#Name#TAG')
        assert game_name == 'Player#Name'
        assert tag_line == 'TAG'


class TestGameFormatting:
    """Test game-related formatting."""

    def test_format_game_duration_simple(self):
        assert format_game_duration(1800) == '30:00'

    def test_format_game_duration_with_seconds(self):
        assert format_game_duration(1534) == '25:34'

    def test_format_game_duration_zero(self):
        assert format_game_duration(0) == '0:00'

    def test_format_game_duration_long(self):
        assert format_game_duration(3661) == '61:01'


class TestKDAFormatting:
    """Test KDA formatting."""

    def test_format_kda_normal(self):
        assert format_kda(10, 3, 7) == '10/3/7'

    def test_format_kda_zero_deaths(self):
        assert format_kda(5, 0, 3) == '5/0/3'

    def test_calculate_kda_ratio_normal(self):
        assert calculate_kda_ratio(10, 3, 7) == 5.67

    def test_calculate_kda_ratio_zero_deaths(self):
        assert calculate_kda_ratio(5, 0, 3) == 8.0

    def test_calculate_kda_ratio_zero_kills(self):
        result = calculate_kda_ratio(0, 5, 0)
        assert result == 0.0


class TestCSFormatting:
    """Test CS (creep score) formatting."""

    def test_format_cs(self):
        assert format_cs(180, 54) == '234 CS'

    def test_format_cs_zero(self):
        assert format_cs(0, 0) == '0 CS'

    def test_calculate_cs_per_min_normal(self):
        assert calculate_cs_per_min(234, 25.5) == 9.18

    def test_calculate_cs_per_min_zero_duration(self):
        assert calculate_cs_per_min(100, 0) == 0.0


class TestGoldFormatting:
    """Test gold formatting."""

    def test_format_gold_thousands(self):
        assert format_gold(12543) == '12.5k'

    def test_format_gold_hundreds(self):
        assert format_gold(987) == '987'

    def test_format_gold_zero(self):
        assert format_gold(0) == '0'

    def test_format_damage_same_as_gold(self):
        assert format_damage(45234) == '45.2k'


class TestTextFormatting:
    """Test text formatting utilities."""

    def test_sanitize_filename_invalid_chars(self):
        result = sanitize_filename('player/name#tag.json')
        assert '/' not in result
        assert '#' not in result

    def test_sanitize_filename_spaces(self):
        result = sanitize_filename('  filename.txt  ')
        assert result == 'filename.txt'

    def test_truncate_text_short(self):
        text = 'Short text'
        assert truncate_text(text, 50) == text

    def test_truncate_text_long(self):
        text = 'This is a very long text that should be truncated'
        result = truncate_text(text, 15)
        assert len(result) == 15
        assert result.endswith('...')

    def test_format_percentage_ratio(self):
        assert format_percentage(0.567) == '56.7%'

    def test_format_percentage_already_percent(self):
        assert format_percentage(75.5) == '75.5%'

    def test_format_number_thousands(self):
        assert format_number(1234567) == '1,234,567'

    def test_format_number_small(self):
        assert format_number(123) == '123'


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_format_kda_negative(self):
        # Should handle gracefully
        result = format_kda(-1, 0, 0)
        assert '-1' in result

    def test_calculate_kda_ratio_all_zero(self):
        result = calculate_kda_ratio(0, 0, 0)
        assert result == 0.0

    def test_format_gold_negative(self):
        result = format_gold(-100)
        assert '-' in str(result)

    def test_truncate_text_zero_length(self):
        with pytest.raises(ValueError):
            truncate_text('text', 0)

    def test_sanitize_filename_empty(self):
        result = sanitize_filename('')
        assert result == ''


@pytest.mark.parametrize('server,expected', [
    ('EUW', 'eu-west'),
    ('NA', 'north-america'),
    ('KR', 'korea'),
    ('EUNE', 'eu-nordic-east'),
])
def test_slugify_server_parametrized(server, expected):
    """Parametrized test for server slugification."""
    assert slugify_server(server) == expected


@pytest.mark.parametrize('duration,expected', [
    (0, '0:00'),
    (60, '1:00'),
    (90, '1:30'),
    (3600, '60:00'),
    (3661, '61:01'),
])
def test_format_game_duration_parametrized(duration, expected):
    """Parametrized test for game duration formatting."""
    assert format_game_duration(duration) == expected


@pytest.mark.parametrize('kills,deaths,assists,expected', [
    (10, 2, 8, 9.0),
    (5, 0, 3, 8.0),
    (0, 0, 0, 0.0),
    (10, 10, 10, 2.0),
])
def test_calculate_kda_ratio_parametrized(kills, deaths, assists, expected):
    """Parametrized test for KDA calculation."""
    assert calculate_kda_ratio(kills, deaths, assists) == expected