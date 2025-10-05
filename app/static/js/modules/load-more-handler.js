// app/static/js/modules/load-more-handler.js
// Handle "Load More" functionality with pagination

(function(window) {
    'use strict';

    /**
     * Load More Handler
     */
    const LoadMoreHandler = {
        /**
         * Initialize load more functionality
         */
        init: function(options) {
            const defaultOptions = {
                buttonSelector: '#load-more-btn',
                containerSelector: '#content-container',
                endpoint: '/api/load-more',
                pageSize: 10,
                onLoad: null,
                onError: null,
                currentPage: 1
            };

            const config = Object.assign({}, defaultOptions, options);
            const button = document.querySelector(config.buttonSelector);

            if (!button) {
                console.warn('Load more button not found:', config.buttonSelector);
                return;
            }

            button.addEventListener('click', function() {
                LoadMoreHandler.loadMore(config);
            });

            return config;
        },

        /**
         * Load more content
         */
        loadMore: function(config) {
            const button = document.querySelector(config.buttonSelector);
            const container = document.querySelector(config.containerSelector);

            if (!button || !container) return;

            // Disable button and show loading state
            button.disabled = true;
            button.classList.add('loading');

            const originalText = button.textContent;
            button.textContent = 'Ładowanie...';

            // Make request
            const url = config.endpoint + '?page=' + config.currentPage;

            fetch(url, {
                method: config.method || 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            })
            .then(function(response) {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(function(data) {
                // Success callback
                if (config.onLoad) {
                    config.onLoad(data, container);
                }

                // Increment page
                config.currentPage++;

                // Hide button if no more data
                if (data.hasMore === false || data.length === 0) {
                    button.style.display = 'none';
                }
            })
            .catch(function(error) {
                console.error('Load more error:', error);

                // Error callback
                if (config.onError) {
                    config.onError(error);
                } else {
                    alert('Błąd podczas ładowania danych');
                }
            })
            .finally(function() {
                // Re-enable button
                button.disabled = false;
                button.classList.remove('loading');
                button.textContent = originalText;
            });
        },

        /**
         * Infinite scroll implementation
         */
        initInfiniteScroll: function(options) {
            const defaultOptions = {
                containerSelector: '#content-container',
                endpoint: '/api/load-more',
                threshold: 200,
                onLoad: null,
                currentPage: 1,
                loading: false,
                hasMore: true
            };

            const config = Object.assign({}, defaultOptions, options);

            window.addEventListener('scroll', window.ClashFinder.throttle(function() {
                if (config.loading || !config.hasMore) return;

                const scrollPosition = window.scrollY + window.innerHeight;
                const documentHeight = document.documentElement.scrollHeight;

                if (scrollPosition >= documentHeight - config.threshold) {
                    LoadMoreHandler.loadMoreInfinite(config);
                }
            }, 250));
        },

        /**
         * Load more for infinite scroll
         */
        loadMoreInfinite: function(config) {
            config.loading = true;

            const container = document.querySelector(config.containerSelector);
            if (!container) return;

            // Show loading indicator
            const loader = LoadMoreHandler.createLoader();
            container.appendChild(loader);

            // Make request
            fetch(config.endpoint + '?page=' + config.currentPage)
                .then(function(response) {
                    return response.json();
                })
                .then(function(data) {
                    // Remove loader
                    loader.remove();

                    // Success callback
                    if (config.onLoad) {
                        config.onLoad(data, container);
                    }

                    // Update state
                    config.currentPage++;
                    config.hasMore = data.hasMore !== false && data.length > 0;
                })
                .catch(function(error) {
                    console.error('Infinite scroll error:', error);
                    loader.remove();
                })
                .finally(function() {
                    config.loading = false;
                });
        },

        /**
         * Create loading indicator
         */
        createLoader: function() {
            const loader = document.createElement('div');
            loader.className = 'loading-indicator';
            loader.innerHTML = `
                <div class="spinner"></div>
                <p>Ładowanie...</p>
            `;
            return loader;
        }
    };

    // Export to window
    window.LoadMoreHandler = LoadMoreHandler;

})(window);