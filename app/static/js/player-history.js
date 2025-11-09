// app/static/js/player-history.js
// Initialization script for player history page

(function() {
    'use strict';

    /**
     * Player History Page Controller
     */
    const PlayerHistoryPage = {
        /**
         * Initialize the page
         */
        init: function() {
            console.log('Initializing Player History Page...');

            // Get player data
            const playerData = PlayerHistoryPage.getPlayerData();
            if (!playerData) {
                console.error('Player data not found');
                return;
            }

            console.log('Player data:', playerData);

            // Initialize progressive loader
            PlayerHistoryPage.initProgressiveLoader(playerData);

            // Initialize load more handler
            PlayerHistoryPage.initLoadMoreHandler(playerData);

            // Setup toggle functionality
            PlayerHistoryPage.setupToggleHandler();

            console.log('Player History Page initialized successfully');
        },

        /**
         * Get player data from DOM
         */
        getPlayerData: function() {
            const playerDataEl = document.getElementById('player-data');
            if (!playerDataEl) return null;

            return {
                summonerName: playerDataEl.dataset.summonerName,
                summonerTag: playerDataEl.dataset.summonerTag,
                server: playerDataEl.dataset.server,
                currentCount: parseInt(playerDataEl.dataset.currentCount || '0')
            };
        },

        /**
         * Initialize progressive loader
         */
        initProgressiveLoader: function(playerData) {
            if (!window.ProgressiveLoader) {
                console.error('ProgressiveLoader module not loaded');
                return;
            }

            ProgressiveLoader.init({
                endpoint: '/player_stats/load_batch',
                containerSelector: '#match-list',
                loadingSelector: '#initial-loading',
                noMatchesSelector: '#no-matches',
                loadMoreContainerSelector: '#load-more-container',
                totalToLoad: 10,
                batchSize: 2,
                delayBetweenBatches: 100,
                animationDelay: 50,
                playerData: playerData,
                statsCallbacks: {
                    onUpdate: function(total, wins, losses) {
                        ProgressiveLoader.updateStatsDisplay(total, wins, losses);
                        // Update player data counter
                        const playerDataEl = document.getElementById('player-data');
                        if (playerDataEl) {
                            playerDataEl.dataset.currentCount = total;
                        }
                    }
                }
            });
        },

/**
 * Initialize load more handler
 */
initLoadMoreHandler: function(playerData) {
    if (!window.LoadMoreHandler) {
        console.error('LoadMoreHandler module not loaded');
        return;
    }

    const name = encodeURIComponent(playerData.summonerName);
    const tag = encodeURIComponent(playerData.summonerTag);
    const server = encodeURIComponent(playerData.server);

    // Zamiast endpoint z page, użyj custom logiki
    const button = document.querySelector('#load-more-btn');
    if (!button) {
        console.error('Load more button not found');
        return;
    }

    button.addEventListener('click', function() {
        // Pobierz aktualną liczbę załadowanych meczów
        const playerDataEl = document.getElementById('player-data');
        const currentCount = parseInt(playerDataEl.dataset.currentCount || '0');
        const container = document.querySelector('#match-list');

        console.log(`Load more clicked | currentCount=${currentCount}`);

        // Znajdź elementy wewnątrz przycisku
        const btnText = button.querySelector('.btn-text');
        const btnLoader = button.querySelector('.btn-loader');

        if (!btnText || !btnLoader) {
            console.warn('Button structure invalid');
            return;
        }

        // Disable button and show loading
        button.disabled = true;
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-flex';

        // Zbuduj URL z start i count
        const url = `/player_stats/load_more_simple?name=${name}&tag=${tag}&server=${server}&start=${currentCount}&count=5`;

        console.log(`Fetching: ${url}`);

        fetch(url, {
            method: 'GET',
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
            const items = data.items || [];

            console.log(`Received ${items.length} new matches`);

            items.forEach(html => {
                const div = document.createElement('div');
                div.innerHTML = html.trim();
                const card = div.firstElementChild;
                if (card) {
                    container.appendChild(card);
                }
            });

            // Update stats after loading more
            const stats = ProgressiveLoader.calculateStats(container);
            ProgressiveLoader.updateStatsDisplay(stats.total, stats.wins, stats.losses);

            // Update player data counter
            if (playerDataEl) {
                playerDataEl.dataset.currentCount = stats.total;
            }

            // Hide button if no more data
            if (data.hasMore === false || items.length === 0) {
                button.parentElement.style.display = 'none';
            }
        })
        .catch(function(error) {
            console.error('Load more failed:', error);
            alert('Błąd podczas ładowania meczów. Spróbuj ponownie.');
        })
        .finally(function() {
            // Re-enable button
            button.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        });
    });

    console.log('Load more handler initialized');
},

        /**
         * Setup match details toggle functionality
         */
        setupToggleHandler: function() {
            // Make toggle function globally available
            window.toggleMatchDetails = function(element) {
                const matchCard = element.closest('.match-card');
                if (!matchCard) {
                    console.warn('Match card not found');
                    return;
                }

                const detailsSection = matchCard.querySelector('.all-players-section');
                const indicator = element.querySelector('.expand-indicator');

                if (!detailsSection) {
                    console.warn('Details section not found');
                    return;
                }

                const isHidden = detailsSection.style.display === 'none' || !detailsSection.style.display;

                if (isHidden) {
                    // Expand
                    detailsSection.style.display = 'block';
                    if (indicator) {
                        indicator.style.transform = 'rotate(180deg)';
                    }
                    element.classList.add('expanded');
                } else {
                    // Collapse
                    detailsSection.style.display = 'none';
                    if (indicator) {
                        indicator.style.transform = 'rotate(0deg)';
                    }
                    element.classList.remove('expanded');
                }
            };

            console.log('Toggle handler setup complete');
        }
    };

    // Auto-initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            PlayerHistoryPage.init();
        });
    } else {
        // DOM already loaded
        PlayerHistoryPage.init();
    }

    // Export for manual initialization if needed
    window.PlayerHistoryPage = PlayerHistoryPage;

})();