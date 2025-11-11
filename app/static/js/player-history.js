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
 * Initialize load more handler with progressive loading
 */
initLoadMoreHandler: function(playerData) {
    if (!window.LoadMoreHandler) {
        console.error('LoadMoreHandler module not loaded');
        return;
    }

    const name = encodeURIComponent(playerData.summonerName);
    const tag = encodeURIComponent(playerData.summonerTag);
    const server = encodeURIComponent(playerData.server);

    const button = document.querySelector('#load-more-btn');
    if (!button) {
        console.error('Load more button not found');
        return;
    }

    button.addEventListener('click', async function() {
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

        try {
            // Progresywne ładowanie 10 meczów po 2 na raz
            const totalToLoad = 10;
            const batchSize = 2;
            const delayBetweenBatches = 100;
            const animationDelay = 50;

            let loadedCount = 0;
            let hasMore = true;

            while (loadedCount < totalToLoad && hasMore) {
                const offset = currentCount + loadedCount;
                const url = `/player_stats/load_more_simple?name=${name}&tag=${tag}&server=${server}&start=${offset}&count=${batchSize}`;

                console.log(`Fetching batch: offset=${offset}, count=${batchSize}`);

                const response = await fetch(url, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }

                const data = await response.json();
                const items = data.items || [];

                console.log(`Received ${items.length} new matches`);

                if (items.length === 0) {
                    hasMore = false;
                    break;
                }

                // Renderuj mecze z animacją
                for (let i = 0; i < items.length; i++) {
                    const htmlString = items[i];
                    const tempDiv = document.createElement('div');
                    tempDiv.innerHTML = htmlString.trim();
                    const card = tempDiv.firstElementChild;

                    if (card) {
                        // Set initial animation state
                        card.style.opacity = '0';
                        card.style.transform = 'translateY(20px)';
                        card.style.transition = 'opacity 0.3s ease-out, transform 0.3s ease-out';

                        // Add to DOM
                        container.appendChild(card);

                        // Small delay before animation
                        await new Promise(resolve => setTimeout(resolve, animationDelay));

                        // Animate in
                        requestAnimationFrame(() => {
                            card.style.opacity = '1';
                            card.style.transform = 'translateY(0)';
                        });
                    }
                }

                loadedCount += items.length;

                // Check if there are more matches
                if (data.hasMore === false || items.length < batchSize) {
                    hasMore = false;
                    break;
                }

                // Delay between batches
                if (loadedCount < totalToLoad && hasMore) {
                    await new Promise(resolve => setTimeout(resolve, delayBetweenBatches));
                }
            }

            // Update stats after loading more
            const stats = ProgressiveLoader.calculateStats(container);
            ProgressiveLoader.updateStatsDisplay(stats.total, stats.wins, stats.losses);

            // Update player data counter
            if (playerDataEl) {
                playerDataEl.dataset.currentCount = stats.total;
            }

            // Hide button if no more data
            if (!hasMore) {
                button.parentElement.style.display = 'none';
            }

        } catch (error) {
            console.error('Load more failed:', error);
            alert('Błąd podczas ładowania meczów. Spróbuj ponownie.');
        } finally {
            // Re-enable button
            button.disabled = false;
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
        }
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