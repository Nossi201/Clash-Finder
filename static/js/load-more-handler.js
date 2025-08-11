// static/js/load-more-handler.js
// Load more matches functionality module

console.log('⬇️ Load More Handler module loaded');

const LoadMoreHandler = {

    init() {
        console.log('🔧 Initializing load more functionality...');
        this.setupEventListener();
        console.log('✅ Load more handler ready');
    },

    setupEventListener() {
        const loadMoreButton = document.getElementById('loadMoreMatchesButton');
        if (!loadMoreButton) {
            console.error('❌ Load more button not found!');
            return;
        }

        loadMoreButton.addEventListener('click', (e) => {
            this.handleLoadMoreClick(e);
        });

        console.log('✅ Load more button listener attached');
    },

    async handleLoadMoreClick(e) {
        const button = e.target;
        console.log('⬇️ Load more button clicked');

        // Disable button during loading
        const originalText = button.textContent;
        button.textContent = 'Loading...';
        button.disabled = true;

        try {
            // Get form data
            const formData = this.getFormData();
            if (!formData) {
                throw new Error('Missing required form data');
            }

            // Get current match count for pagination
            formData.current_count = document.querySelectorAll('.card').length;

            console.log('📤 Request data:', formData);

            // Make API request
            const newMatches = await this.fetchNewMatches(formData);

            if (newMatches && newMatches.length > 0) {
                console.log(`📥 Received ${newMatches.length} new matches`);

                // Render and add each new match
                await this.renderAndAddMatches(newMatches, formData.current_count);

                console.log(`✅ Successfully added ${newMatches.length} new matches`);
            } else {
                console.log('ℹ️ No more matches available');
                button.textContent = 'No more matches';
                button.disabled = true;
                return;
            }

        } catch (error) {
            console.error('❌ Load more error:', error);
            alert(`Error loading more matches: ${error.message}`);
        } finally {
            // Re-enable button if not permanently disabled
            if (button.textContent !== 'No more matches') {
                button.textContent = originalText;
                button.disabled = false;
            }
        }
    },

    getFormData() {
        console.log('📋 Getting form data...');

        const serverInput = document.getElementById('server');
        const summonerNameInput = document.getElementById('summonerName');
        const summonerTagInput = document.getElementById('summonerTag');
        const numberSelect = document.getElementById('number-list');

        // Validate required inputs
        if (!serverInput || !summonerNameInput || !summonerTagInput) {
            console.error('❌ Missing required form inputs:', {
                server: !!serverInput,
                summonerName: !!summonerNameInput,
                summonerTag: !!summonerTagInput
            });
            return null;
        }

        const formData = {
            server: serverInput.value,
            SUMMONER_NAME: summonerNameInput.value,
            SUMMONER_TAG: summonerTagInput.value,
            number: parseInt(numberSelect?.value || 10)
        };

        console.log('✅ Form data collected:', formData);
        return formData;
    },

    async fetchNewMatches(formData) {
        console.log('🌐 Fetching new matches from API...');

        const response = await fetch('/load_more_matches', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('✅ API response received');
        return data;
    },

    async renderAndAddMatches(newMatches, startIndex) {
        console.log('🎨 Rendering and adding new matches...');

        let successCount = 0;
        let errorCount = 0;

        for (let i = 0; i < newMatches.length; i++) {
            try {
                const matchIndex = startIndex + i + 1;
                console.log(`🎨 Rendering match ${matchIndex}...`);

                // Render match with CDN images
                const matchHtml = await MatchRenderer.renderMatchCard(newMatches[i], matchIndex);

                // Add to DOM
                const success = MatchRenderer.addMatchToDOM(matchHtml);

                if (success) {
                    successCount++;
                    console.log(`✅ Match ${matchIndex} added successfully`);
                } else {
                    errorCount++;
                    console.error(`❌ Failed to add match ${matchIndex} to DOM`);
                }

            } catch (error) {
                errorCount++;
                console.error(`❌ Error rendering match ${i + 1}:`, error);
            }
        }

        console.log(`📊 Rendering complete: ${successCount} success, ${errorCount} errors`);

        // If we successfully added matches, ensure toggle handlers work
        if (successCount > 0) {
            console.log('🔄 Ensuring toggle functionality for new matches...');
            // Since we use event delegation, no need to re-initialize
            // But we can run a quick check
            this.validateNewToggles();
        }

        return successCount;
    },

    validateNewToggles() {
        console.log('🔍 Validating toggle functionality for new matches...');

        const allCards = document.querySelectorAll('.card');
        let validToggleCount = 0;

        allCards.forEach((card, index) => {
            const button = card.querySelector('.toggle-details');
            const detailedRow = card.querySelector('.row.margin-0');

            if (button && detailedRow) {
                // Ensure proper initial state
                if (!detailedRow.hasAttribute('hidden')) {
                    detailedRow.setAttribute('hidden', '');
                }
                if (button.textContent.includes('Hide')) {
                    button.textContent = 'Show Stats';
                }
                validToggleCount++;
            }
        });

        console.log(`✅ Validated ${validToggleCount} toggle buttons`);
        return validToggleCount;
    },

    // Debug helpers
    getCurrentMatchCount() {
        return document.querySelectorAll('.card').length;
    },

    getButtonState() {
        const button = document.getElementById('loadMoreMatchesButton');
        return {
            exists: !!button,
            text: button?.textContent,
            disabled: button?.disabled
        };
    },

    // Test load more without rendering (for debugging)
    async testLoadMoreAPI() {
        console.log('🧪 Testing load more API...');

        try {
            const formData = this.getFormData();
            if (!formData) {
                throw new Error('Form data not available');
            }

            formData.current_count = this.getCurrentMatchCount();

            const result = await this.fetchNewMatches(formData);
            console.log('✅ API test successful:', result?.length || 0, 'matches');
            return result;

        } catch (error) {
            console.error('❌ API test failed:', error);
            return null;
        }
    },

    // Force reset button state
    resetButton() {
        const button = document.getElementById('loadMoreMatchesButton');
        if (button) {
            button.textContent = 'Show more';
            button.disabled = false;
            console.log('🔄 Button state reset');
        }
    }
};

// Make LoadMoreHandler available globally
window.LoadMoreHandler = LoadMoreHandler;