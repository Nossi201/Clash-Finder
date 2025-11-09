// app/static/js/modules/progressive-loader.js
// Progressive match loading with smooth animations

(function(window) {
    'use strict';

    /**
     * Progressive Loader - loads content in batches with animations
     */
    const ProgressiveLoader = {
        /**
         * Initialize progressive loading
         */
        init: function(options) {
            const config = {
                endpoint: '/player_stats/load_batch',
                containerSelector: '#match-list',
                loadingSelector: '#initial-loading',
                noMatchesSelector: '#no-matches',
                loadMoreContainerSelector: '#load-more-container',
                statsCallbacks: {
                    onUpdate: null  // callback(total, wins, losses)
                },
                totalToLoad: 10,
                batchSize: 2,
                delayBetweenBatches: 100,  // ms
                animationDelay: 50,  // ms per card
                playerData: {},
                ...options
            };

            const state = {
                currentOffset: 0,
                isLoading: false,
                hasMore: true
            };

            // Get DOM elements
            const container = document.querySelector(config.containerSelector);
            const loadingIndicator = document.querySelector(config.loadingSelector);
            const noMatchesDiv = document.querySelector(config.noMatchesSelector);
            const loadMoreContainer = document.querySelector(config.loadMoreContainerSelector);

            if (!container) {
                console.error('Container not found:', config.containerSelector);
                return null;
            }

            // Start loading
            ProgressiveLoader.startLoading(config, state, {
                container,
                loadingIndicator,
                noMatchesDiv,
                loadMoreContainer
            });

            return { config, state };
        },

        /**
         * Start progressive loading
         */
        startLoading: async function(config, state, elements) {
            const { container, loadingIndicator, noMatchesDiv, loadMoreContainer } = elements;

            // Show loading
            if (loadingIndicator) loadingIndicator.style.display = 'block';
            if (container) container.style.display = 'none';

            console.log('Starting progressive loading...', config.playerData);

            try {
                // Load batches progressively
                while (state.currentOffset < config.totalToLoad && !state.isLoading) {
                    state.isLoading = true;

                    const batchPayload = {
                        SUMMONER_NAME: config.playerData.summonerName,
                        SUMMONER_TAG: config.playerData.summonerTag,
                        server: config.playerData.server,
                        offset: state.currentOffset,
                        batch_size: config.batchSize
                    };

                    console.log(`Fetching batch at offset ${state.currentOffset}...`);

                    const response = await fetch(config.endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(batchPayload)
                    });

                    if (!response.ok) {
                        console.error('Batch request failed:', response.status);
                        break;
                    }

                    const data = await response.json();
                    console.log(`Received ${data.matches?.length || 0} matches`);

                    if (data.matches && data.matches.length > 0) {
                        // Show container on first batch
                        if (state.currentOffset === 0) {
                            if (loadingIndicator) loadingIndicator.style.display = 'none';
                            if (container) container.style.display = 'block';
                        }

                        // Render batch with animations
                        await ProgressiveLoader.renderBatch(
                            data.matches,
                            container,
                            config.animationDelay
                        );

                        state.currentOffset = data.offset;

                        // Update stats if callback provided
                        if (config.statsCallbacks.onUpdate) {
                            const stats = ProgressiveLoader.calculateStats(container);
                            config.statsCallbacks.onUpdate(stats.total, stats.wins, stats.losses);
                        }

                        // Delay between batches
                        await new Promise(resolve => setTimeout(resolve, config.delayBetweenBatches));
                    } else {
                        console.log('No more matches in batch');
                        break;
                    }

                    state.isLoading = false;

                    if (!data.has_more) {
                        console.log('No more matches available');
                        break;
                    }
                }

                // Hide loading indicator
                if (loadingIndicator) loadingIndicator.style.display = 'none';

                console.log(`Loading complete! Total matches: ${container.children.length}`);

                // Show load more button if applicable
                if (state.currentOffset >= config.totalToLoad && loadMoreContainer) {
                    loadMoreContainer.style.display = 'block';
                    state.hasMore = true;
                }

                // Show no matches message if empty
                if (container.children.length === 0 && noMatchesDiv) {
                    noMatchesDiv.style.display = 'block';
                }

            } catch (error) {
                console.error('Error during progressive loading:', error);
                if (loadingIndicator) loadingIndicator.style.display = 'none';
                if (noMatchesDiv) noMatchesDiv.style.display = 'block';
            }
        },

        /**
         * Render batch of matches with animations
         */
        renderBatch: async function(matchesHtml, container, animationDelay) {
            for (let i = 0; i < matchesHtml.length; i++) {
                const htmlString = matchesHtml[i];

                // Create temporary container
                const tempDiv = document.createElement('div');
                tempDiv.innerHTML = htmlString.trim();

                // Get the actual card element
                const card = tempDiv.firstElementChild;

                if (!card) {
                    console.error('No card element found in HTML');
                    continue;
                }

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
        },

        /**
         * Calculate statistics from rendered matches
         */
        calculateStats: function(container) {
            const cards = container.querySelectorAll('.match-card');
            const total = cards.length;
            const wins = Array.from(cards).filter(c => c.classList.contains('match-win')).length;
            const losses = total - wins;

            return { total, wins, losses };
        },

        /**
         * Update statistics display
         */
        updateStatsDisplay: function(total, wins, losses) {
            const winRate = total > 0 ? Math.round((wins / total) * 100) : 0;

            const elements = {
                total: document.getElementById('total-matches'),
                wins: document.getElementById('total-wins'),
                losses: document.getElementById('total-losses'),
                winRate: document.getElementById('win-rate')
            };

            if (elements.total) elements.total.textContent = total;
            if (elements.wins) elements.wins.textContent = wins + 'W';
            if (elements.losses) elements.losses.textContent = losses + 'L';
            if (elements.winRate) elements.winRate.textContent = winRate + '%';
        }
    };

    // Export to window
    window.ProgressiveLoader = ProgressiveLoader;

})(window);