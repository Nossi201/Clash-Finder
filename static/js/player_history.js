// static/js/player_history.js
// Main player history JavaScript file - orchestrates all modules

console.log('🚀 Player History Main module loaded');

// Main application object
const PlayerHistoryApp = {

    // Initialize the entire application
    async init() {
        console.log('🎬 Initializing Player History App...');

        try {
            // Step 1: Initialize CDN caches
            await this.initializeCDN();

            // Step 2: Initialize UI handlers
            this.initializeHandlers();

            // Step 3: Run diagnostics
            this.runDiagnostics();

            console.log('✅ Player History App initialized successfully');

        } catch (error) {
            console.error('❌ Failed to initialize Player History App:', error);
            this.handleInitializationError(error);
        }
    },

    async initializeCDN() {
        console.log('📡 Initializing CDN...');

        if (typeof CDNUtils === 'undefined') {
            throw new Error('CDNUtils module not loaded');
        }

        const success = await CDNUtils.initialize();
        if (!success) {
            console.warn('⚠️ CDN initialization had issues, but continuing...');
        }

        console.log('✅ CDN initialized');
    },

    initializeHandlers() {
        console.log('🎮 Initializing handlers...');

        // Check if modules are loaded
        if (typeof ToggleHandler === 'undefined') {
            throw new Error('ToggleHandler module not loaded');
        }

        if (typeof LoadMoreHandler === 'undefined') {
            throw new Error('LoadMoreHandler module not loaded');
        }

        // Initialize handlers
        ToggleHandler.init();
        LoadMoreHandler.init();

        console.log('✅ Handlers initialized');
    },

    runDiagnostics() {
        console.log('🔍 Running diagnostics...');

        const diagnostics = {
            cards: document.querySelectorAll('.card').length,
            toggleButtons: document.querySelectorAll('.toggle-details').length,
            loadMoreButton: !!document.getElementById('loadMoreMatchesButton'),
            formInputs: {
                server: !!document.getElementById('server'),
                summonerName: !!document.getElementById('summonerName'),
                summonerTag: !!document.getElementById('summonerTag')
            }
        };

        console.log('📊 Diagnostics:', diagnostics);

        // Store diagnostics for debugging
        this.diagnostics = diagnostics;

        // Validate critical elements
        if (diagnostics.cards === 0) {
            console.warn('⚠️ No match cards found');
        }

        if (diagnostics.toggleButtons === 0) {
            console.warn('⚠️ No toggle buttons found');
        }

        if (!diagnostics.loadMoreButton) {
            console.warn('⚠️ Load more button not found');
        }

        console.log('✅ Diagnostics complete');
    },

    handleInitializationError(error) {
        console.error('💥 Initialization error:', error.message);

        // Try to set up minimal functionality
        console.log('🆘 Setting up fallback functionality...');

        try {
            this.setupFallbackToggle();
            this.setupFallbackLoadMore();
            console.log('✅ Fallback functionality ready');
        } catch (fallbackError) {
            console.error('💀 Even fallback failed:', fallbackError);
        }
    },

    setupFallbackToggle() {
        console.log('🔧 Setting up fallback toggle...');

        document.addEventListener('click', function(e) {
            if (e.target.classList.contains('toggle-details')) {
                console.log('🎯 Fallback toggle clicked');

                const card = e.target.closest('.card');
                const rows = card?.querySelectorAll('.row');
                const detailedRow = rows?.[1]; // Second row

                if (detailedRow) {
                    if (detailedRow.hasAttribute('hidden')) {
                        detailedRow.removeAttribute('hidden');
                        e.target.textContent = 'Hide Stats';
                    } else {
                        detailedRow.setAttribute('hidden', '');
                        e.target.textContent = 'Show Stats';
                    }
                }
            }
        });
    },

    setupFallbackLoadMore() {
        console.log('🔧 Setting up fallback load more...');

        const button = document.getElementById('loadMoreMatchesButton');
        if (button) {
            button.onclick = function() {
                alert('Load more functionality temporarily unavailable. Please refresh the page.');
            };
        }
    },

    // Debug helpers
    getStatus() {
        return {
            initialized: !!this.diagnostics,
            diagnostics: this.diagnostics,
            modules: {
                CDNUtils: typeof CDNUtils !== 'undefined',
                ToggleHandler: typeof ToggleHandler !== 'undefined',
                LoadMoreHandler: typeof LoadMoreHandler !== 'undefined',
                MatchRenderer: typeof MatchRenderer !== 'undefined'
            },
            handlers: {
                toggleStatus: ToggleHandler?.getToggleStatus?.() || 'Not available',
                loadMoreStatus: LoadMoreHandler?.getButtonState?.() || 'Not available'
            }
        };
    },

    // Manual test functions
    testToggle(cardIndex = 0) {
        if (typeof ToggleHandler !== 'undefined') {
            return ToggleHandler.debugToggle(cardIndex);
        }
        console.error('ToggleHandler not available');
        return false;
    },

    async testLoadMore() {
        if (typeof LoadMoreHandler !== 'undefined') {
            return await LoadMoreHandler.testLoadMoreAPI();
        }
        console.error('LoadMoreHandler not available');
        return null;
    },

    fixAllToggles() {
        if (typeof ToggleHandler !== 'undefined') {
            return ToggleHandler.fixAllToggleStates();
        }
        console.error('ToggleHandler not available');
        return 0;
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('📄 DOM loaded, starting initialization...');

    // Small delay to ensure all modules are loaded
    setTimeout(() => {
        PlayerHistoryApp.init();
    }, 100);
});

// Make available globally for debugging
window.PlayerHistoryApp = PlayerHistoryApp;

// Legacy support - expose key functions globally for backward compatibility
window.playerHistoryDebug = {
    getStatus: () => PlayerHistoryApp.getStatus(),
    testToggle: (cardIndex) => PlayerHistoryApp.testToggle(cardIndex),
    testLoadMore: () => PlayerHistoryApp.testLoadMore(),
    fixAllToggles: () => PlayerHistoryApp.fixAllToggles(),

    // Direct module access
    CDNUtils: () => window.CDNUtils,
    ToggleHandler: () => window.ToggleHandler,
    LoadMoreHandler: () => window.LoadMoreHandler,
    MatchRenderer: () => window.MatchRenderer
};

console.log('🔧 Debug available: window.PlayerHistoryApp, window.playerHistoryDebug');