# tests/unit/test_validators.py
"""
Unit tests for validation utilities.
"""

import pytest
from app.utils.validators import (
    ValidationError,
    validate_riot_id,
    validate_server,
    validate_match_count,
    validate_email,
    validate_puuid,
    validate_json_structure,
    validate_api_response,
    validate_champion_id,
    validate_item_id,
    validate_queue_id,
    sanitize_input,
    validate_pagination,
    is_valid_url
)


class TestRiotIDValidation:
    """Test Riot ID validation."""

    def test_valid_riot_id(self):
        is_valid, error = validate_riot_id('PlayerName', 'EUW1')
        assert is_valid is True
        assert error is None

    def test_riot_id_empty_name(self):
        is_valid, error = validate_riot_id('', 'TAG')
        assert is_valid is False
        assert 'empty' in error.lower()

    def test_riot_id_short_name(self):
        is_valid, error = validate_riot_id('AB', 'TAG')
        assert is_valid is False
        assert '3 characters' in error

    def test_riot_id_long_name(self):
        is_valid, error = validate_riot_id('A' * 17, 'TAG')
        assert is_valid is False
        assert '16 characters' in error

    def test_riot_id_invalid_chars(self):
        is_valid, error = validate_riot_id('Player@Name!', 'TAG')
        assert is_valid is False
        assert 'invalid characters' in error.lower()

    def test_riot_id_short_tag(self):
        is_valid, error = validate_riot_id('PlayerName', 'AB')
        assert is_valid is False
        assert 'Tag line must be at least 3' in error

    def test_riot_id_long_tag(self):
        is_valid, error = validate_riot_id('PlayerName', 'ABCDEF')
        assert is_valid is False
        assert '5 characters' in error

    def test_riot_id_valid_with_spaces(self):
        is_valid, error = validate_riot_id('Player Name', 'TAG')
        assert is_valid is True

    def test_riot_id_optional_tag(self):
        is_valid, error = validate_riot_id('PlayerName', '')
        assert is_valid is True


class TestServerValidation:
    """Test server validation."""

    def test_valid_server_euw(self):
        is_valid, error = validate_server('EUW')
        assert is_valid is True
        assert error is None

    def test_valid_server_lowercase(self):
        is_valid, error = validate_server('euw')
        assert is_valid is True

    def test_invalid_server(self):
        is_valid, error = validate_server('INVALID')
        assert is_valid is False
        assert 'Invalid server' in error

    def test_empty_server(self):
        is_valid, error = validate_server('')
        assert is_valid is False
        assert 'empty' in error.lower()

    @pytest.mark.parametrize('server', [
        'EUW', 'EUNE', 'NA', 'KR', 'BR', 'LAN', 'LAS', 'OCE', 'TR', 'RU'
    ])
    def test_all_valid_servers(self, server):
        is_valid, error = validate_server(server)
        assert is_valid is True


class TestMatchCountValidation:
    """Test match count validation."""

    def test_valid_match_count(self):
        is_valid, error = validate_match_count(20)
        assert is_valid is True

    def test_zero_match_count(self):
        is_valid, error = validate_match_count(0)
        assert is_valid is False
        assert 'positive' in error.lower()

    def test_negative_match_count(self):
        is_valid, error = validate_match_count(-5)
        assert is_valid is False

    def test_exceed_max_count(self):
        is_valid, error = validate_match_count(150, max_count=100)
        assert is_valid is False
        assert '100' in error

    def test_custom_max_count(self):
        is_valid, error = validate_match_count(50, max_count=50)
        assert is_valid is True


class TestEmailValidation:
    """Test email validation."""

    def test_valid_email(self):
        is_valid, error = validate_email('user@example.com')
        assert is_valid is True

    def test_invalid_email_no_at(self):
        is_valid, error = validate_email('userexample.com')
        assert is_valid is False

    def test_invalid_email_no_domain(self):
        is_valid, error = validate_email('user@')
        assert is_valid is False

    def test_empty_email(self):
        is_valid, error = validate_email('')
        assert is_valid is False

    @pytest.mark.parametrize('email', [
        'user@example.com',
        'user.name@example.com',
        'user+tag@example.co.uk',
        'user_123@test-domain.org'
    ])
    def test_various_valid_emails(self, email):
        is_valid, error = validate_email(email)
        assert is_valid is True


class TestPUUIDValidation:
    """Test PUUID validation."""

    def test_valid_puuid(self):
        is_valid, error = validate_puuid('abcd1234-ef56-7890-abcd-1234567890ab')
        assert is_valid is True

    def test_empty_puuid(self):
        is_valid, error = validate_puuid('')
        assert is_valid is False

    def test_short_puuid(self):
        is_valid, error = validate_puuid('abc')
        assert is_valid is False

    def test_long_puuid(self):
        is_valid, error = validate_puuid('a' * 150)
        assert is_valid is False

    def test_puuid_with_invalid_chars(self):
        is_valid, error = validate_puuid('test@puuid#invalid!')
        assert is_valid is False


class TestJSONValidation:
    """Test JSON structure validation."""

    def test_valid_json_structure(self):
        data = {'name': 'test', 'id': 123}
        is_valid, error = validate_json_structure(data, ['name', 'id'])
        assert is_valid is True

    def test_missing_required_field(self):
        data = {'name': 'test'}
        is_valid, error = validate_json_structure(data, ['name', 'id'])
        assert is_valid is False
        assert 'Missing required field' in error

    def test_not_a_dict(self):
        is_valid, error = validate_json_structure(['list'], ['field'])
        assert is_valid is False
        assert 'dictionary' in error.lower()

    def test_empty_required_fields(self):
        data = {'name': 'test'}
        is_valid, error = validate_json_structure(data, [])
        assert is_valid is True


class TestAPIResponseValidation:
    """Test API response validation."""

    def test_valid_api_response(self):
        response = {'puuid': 'abc', 'gameName': 'test'}
        assert validate_api_response(response, ['puuid']) is True

    def test_invalid_api_response_missing_key(self):
        response = {'gameName': 'test'}
        assert validate_api_response(response, ['puuid']) is False

    def test_invalid_api_response_not_dict(self):
        assert validate_api_response(['list'], ['key']) is False

    def test_invalid_api_response_none(self):
        assert validate_api_response(None, ['key']) is False


class TestGameIDValidation:
    """Test game ID validation."""

    def test_valid_champion_id(self):
        is_valid, error = validate_champion_id(266)
        assert is_valid is True

    def test_invalid_champion_id_negative(self):
        is_valid, error = validate_champion_id(-1)
        assert is_valid is False

    def test_invalid_champion_id_zero(self):
        is_valid, error = validate_champion_id(0)
        assert is_valid is False

    def test_champion_id_out_of_range(self):
        is_valid, error = validate_champion_id(9999)
        assert is_valid is False

    def test_valid_item_id(self):
        is_valid, error = validate_item_id(3153)
        assert is_valid is True

    def test_valid_item_id_zero(self):
        is_valid, error = validate_item_id(0)
        assert is_valid is True

    def test_invalid_item_id_negative(self):
        is_valid, error = validate_item_id(-1)
        assert is_valid is False

    def test_valid_queue_id(self):
        is_valid, error = validate_queue_id(420)
        assert is_valid is True

    def test_invalid_queue_id_negative(self):
        is_valid, error = validate_queue_id(-1)
        assert is_valid is False


class TestInputSanitization:
    """Test input sanitization."""

    def test_sanitize_basic_text(self):
        result = sanitize_input('  Test Input  ')
        assert result == 'Test Input'

    def test_sanitize_html_tags(self):
        result = sanitize_input('<script>alert("xss")</script>')
        assert '<script>' not in result
        assert 'alert' in result

    def test_sanitize_special_chars(self):
        result = sanitize_input('Test<>"\'"')
        assert '<' not in result
        assert '>' not in result

    def test_sanitize_max_length(self):
        long_text = 'a' * 200
        result = sanitize_input(long_text, max_length=50)
        assert len(result) == 50


class TestPaginationValidation:
    """Test pagination validation."""

    def test_valid_pagination(self):
        is_valid, error = validate_pagination(0, 20)
        assert is_valid is True

    def test_invalid_pagination_negative_start(self):
        is_valid, error = validate_pagination(-1, 20)
        assert is_valid is False

    def test_invalid_pagination_zero_count(self):
        is_valid, error = validate_pagination(0, 0)
        assert is_valid is False

    def test_invalid_pagination_exceed_max(self):
        is_valid, error = validate_pagination(0, 150, max_count=100)
        assert is_valid is False


class TestURLValidation:
    """Test URL validation."""

    def test_valid_http_url(self):
        assert is_valid_url('http://example.com') is True

    def test_valid_https_url(self):
        assert is_valid_url('https://example.com') is True

    def test_invalid_url_no_protocol(self):
        assert is_valid_url('example.com') is False

    def test_invalid_url_not_url(self):
        assert is_valid_url('not-a-url') is False

    @pytest.mark.parametrize('url', [
        'https://www.example.com',
        'http://subdomain.example.com',
        'https://example.com/path/to/page',
        'http://localhost:8000',
        'https://192.168.1.1'
    ])
    def test_various_valid_urls(self, url):
        assert is_valid_url(url) is True


class TestEdgeCases:
    """Test edge cases."""

    def test_validate_riot_id_whitespace_only(self):
        is_valid, error = validate_riot_id('   ', 'TAG')
        assert is_valid is False

    def test_validate_email_whitespace(self):
        is_valid, error = validate_email('  user@example.com  ')
        # Should handle whitespace gracefully
        assert error is not None

    def test_sanitize_input_unicode(self):
        result = sanitize_input('Tëst Ûñíçödé')
        assert 'Tëst' in result

    def test_validate_json_extra_fields(self):
        data = {'name': 'test', 'id': 123, 'extra': 'field'}
        is_valid, error = validate_json_structure(data, ['name', 'id'])
        assert is_valid is True  # Extra fields are OK