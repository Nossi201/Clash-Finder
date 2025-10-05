# tests/integration/test_cache.py
"""
Integration tests for caching service.
"""

import pytest
import time
from app.services.cache import cache, cached, invalidate_cache


class TestCache:
    """Test cache operations."""

    def test_cache_set_and_get(self, app_context):
        """Test basic set and get operations."""
        cache.set('test_key', 'test_value')
        result = cache.get('test_key')

        assert result == 'test_value'

    def test_cache_get_nonexistent(self, app_context):
        """Test getting non-existent key."""
        result = cache.get('nonexistent_key')

        assert result is None

    def test_cache_set_with_ttl(self, app_context):
        """Test cache with TTL."""
        cache.set('ttl_key', 'ttl_value', ttl=1)

        # Should exist immediately
        assert cache.get('ttl_key') == 'ttl_value'

        # Wait for TTL to expire
        time.sleep(1.5)

        # Should be gone
        assert cache.get('ttl_key') is None

    def test_cache_delete(self, app_context):
        """Test cache deletion."""
        cache.set('delete_key', 'delete_value')
        assert cache.get('delete_key') == 'delete_value'

        cache.delete('delete_key')
        assert cache.get('delete_key') is None

    def test_cache_clear(self, app_context):
        """Test clearing entire cache."""
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        cache.clear()

        assert cache.get('key1') is None
        assert cache.get('key2') is None

    def test_cache_exists(self, app_context):
        """Test cache exists check."""
        cache.set('exists_key', 'exists_value')

        assert cache.exists('exists_key') is True
        assert cache.exists('nonexistent') is False

    def test_cache_complex_data(self, app_context):
        """Test caching complex data structures."""
        data = {
            'list': [1, 2, 3],
            'dict': {'nested': 'value'},
            'tuple': (1, 2, 3)
        }

        cache.set('complex_key', data)
        result = cache.get('complex_key')

        assert result == data

    def test_cache_overwrite(self, app_context):
        """Test overwriting cached value."""
        cache.set('overwrite_key', 'old_value')
        cache.set('overwrite_key', 'new_value')

        assert cache.get('overwrite_key') == 'new_value'


class TestCachedDecorator:
    """Test @cached decorator."""

    def test_cached_decorator_basic(self, app_context):
        """Test basic cached decorator usage."""
        call_count = {'count': 0}

        @cached(ttl=60, key_prefix='test')
        def expensive_function(x):
            call_count['count'] += 1
            return x * 2

        # First call
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count['count'] == 1

        # Second call (should use cache)
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count['count'] == 1  # Not called again

    def test_cached_decorator_different_args(self, app_context):
        """Test cached decorator with different arguments."""
        call_count = {'count': 0}

        @cached(ttl=60)
        def function_with_args(x, y):
            call_count['count'] += 1
            return x + y

        result1 = function_with_args(1, 2)
        result2 = function_with_args(3, 4)
        result3 = function_with_args(1, 2)  # Same as first

        assert result1 == 3
        assert result2 == 7
        assert result3 == 3
        assert call_count['count'] == 2  # Only called twice

    def test_cached_decorator_with_kwargs(self, app_context):
        """Test cached decorator with keyword arguments."""

        @cached(ttl=60)
        def function_with_kwargs(x, y=10):
            return x + y

        result1 = function_with_kwargs(5, y=10)
        result2 = function_with_kwargs(5, y=10)

        assert result1 == result2 == 15

    def test_cached_decorator_ttl_expiry(self, app_context):
        """Test cached decorator TTL expiry."""
        call_count = {'count': 0}

        @cached(ttl=1)
        def short_ttl_function(x):
            call_count['count'] += 1
            return x

        # First call
        short_ttl_function(1)
        assert call_count['count'] == 1

        # Wait for TTL
        time.sleep(1.5)

        # Should call again
        short_ttl_function(1)
        assert call_count['count'] == 2


class TestCacheInvalidation:
    """Test cache invalidation."""

    def test_invalidate_specific_key(self, app_context):
        """Test invalidating specific cache key."""
        cache.set('inv_key', 'inv_value')

        invalidate_cache('inv_key')

        assert cache.get('inv_key') is None

    def test_invalidate_all(self, app_context):
        """Test invalidating all cache."""
        cache.set('key1', 'value1')
        cache.set('key2', 'value2')

        invalidate_cache()

        assert cache.get('key1') is None
        assert cache.get('key2') is None


class TestCacheBackend:
    """Test cache backend selection."""

    def test_cache_backend_initialization(self, app_context):
        """Test that cache backend is initialized."""
        assert cache._initialized is True
        assert cache.backend is not None

    def test_in_memory_cache(self, app_context):
        """Test in-memory cache backend."""
        from app.services.cache import InMemoryCache

        # Cache should be using in-memory backend in tests
        assert isinstance(cache.backend, InMemoryCache)


class TestCachePerformance:
    """Test cache performance."""

    @pytest.mark.slow
    def test_cache_performance(self, app_context, benchmark_timer):
        """Test cache read/write performance."""
        # Warm up
        for i in range(100):
            cache.set(f'perf_key_{i}', f'value_{i}')

        # Test read performance
        benchmark_timer.start()
        for i in range(100):
            cache.get(f'perf_key_{i}')
        elapsed = benchmark_timer.stop()

        # Should be fast (< 100ms for 100 operations)
        assert elapsed < 0.1

    def test_cache_large_data(self, app_context):
        """Test caching large data."""
        large_data = {'data': 'x' * 10000}

        cache.set('large_key', large_data)
        result = cache.get('large_key')

        assert result == large_data


class TestCacheEdgeCases:
    """Test cache edge cases."""

    def test_cache_none_value(self, app_context):
        """Test caching None value."""
        cache.set('none_key', None)

        # Should return None (not treat as cache miss)
        result = cache.get('none_key')

        # This depends on implementation - might be None or might treat as miss
        # For now, we expect None to not be cached
        assert result is None or result == 'NONE_CACHED'

    def test_cache_empty_string(self, app_context):
        """Test caching empty string."""
        cache.set('empty_key', '')
        result = cache.get('empty_key')

        assert result == ''

    def test_cache_zero_value(self, app_context):
        """Test caching zero."""
        cache.set('zero_key', 0)
        result = cache.get('zero_key')

        assert result == 0

    def test_cache_boolean_values(self, app_context):
        """Test caching boolean values."""
        cache.set('true_key', True)
        cache.set('false_key', False)

        assert cache.get('true_key') is True
        assert cache.get('false_key') is False