// static/js/toggle-handler.js
// Toggle stats functionality module

console.log('🎯 Toggle Handler module loaded');

const ToggleHandler = {

    init() {
        console.log('🔧 Initializing toggle functionality...');
        this.setupEventListeners();
        console.log('✅ Toggle handler ready');
    },

    setupEventListeners() {
        // Use event delegation to handle both existing and dynamically added buttons
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('toggle-details')) {
                this.handleToggleClick(e);
            }
        });
    },

    handleToggleClick(e) {
        const button = e.target;
        const buttonId = button.id;

        console.log('🎯 Toggle button clicked:', buttonId);

        // Find the card containing this button
        const card = button.closest('.card');
        if (!card) {
            console.error('❌ Card not found for button:', buttonId);
            return;
        }

        // Find the detailed stats row
        const detailedRow = this.findDetailedStatsRow(card);
        if (!detailedRow) {
            console.error('❌ Detailed stats row not found for button:', buttonId);
            return;
        }

        // Toggle the stats
        this.toggleStats(detailedRow, button);
    },

    findDetailedStatsRow(card) {
        // Method 1: Look for row with hidden attribute
        let detailedRow = card.querySelector('.row[hidden]');

        if (!detailedRow) {
            // Method 2: Look for row with class "margin-0" (detailed stats indicator)
            detailedRow = card.querySelector('.row.margin-0');
        }

        if (!detailedRow) {
            // Method 3: Get all rows and take the second one (fallback)
            const allRows = card.querySelectorAll('.row');
            if (allRows.length >= 2) {
                detailedRow = allRows[1];
            }
        }

        // Debug info
        if (detailedRow) {
            console.log('✅ Found detailed row:', {
                hasHidden: detailedRow.hasAttribute('hidden'),
                hasMargin0: detailedRow.classList.contains('margin-0'),
                classes: detailedRow.className
            });
        }

        return detailedRow;
    },

    toggleStats(detailedRow, button) {
        const isHidden = detailedRow.hasAttribute('hidden');

        if (isHidden) {
            // Show stats
            detailedRow.removeAttribute('hidden');
            button.textContent = 'Hide Stats';
            console.log('✅ Stats shown');
        } else {
            // Hide stats
            detailedRow.setAttribute('hidden', '');
            button.textContent = 'Show Stats';
            console.log('✅ Stats hidden');
        }
    },

    // Manual toggle for debugging
    debugToggle(cardIndex = 0) {
        const cards = document.querySelectorAll('.card');
        if (cards[cardIndex]) {
            const button = cards[cardIndex].querySelector('.toggle-details');
            if (button) {
                button.click();
                return true;
            }
        }
        return false;
    },

    // Check toggle status for all cards
    getToggleStatus() {
        const cards = document.querySelectorAll('.card');
        const status = [];

        cards.forEach((card, index) => {
            const button = card.querySelector('.toggle-details');
            const detailedRow = this.findDetailedStatsRow(card);

            status.push({
                index,
                buttonExists: !!button,
                buttonText: button?.textContent,
                detailedRowExists: !!detailedRow,
                isHidden: detailedRow?.hasAttribute('hidden')
            });
        });

        return status;
    },

    // Fix all toggle states (debugging helper)
    fixAllToggleStates() {
        console.log('🔧 Fixing all toggle states...');

        const cards = document.querySelectorAll('.card');
        let fixed = 0;

        cards.forEach((card, index) => {
            const button = card.querySelector('.toggle-details');
            const detailedRow = this.findDetailedStatsRow(card);

            if (button && detailedRow) {
                // Ensure proper initial state
                if (!detailedRow.hasAttribute('hidden')) {
                    detailedRow.setAttribute('hidden', '');
                }
                button.textContent = 'Show Stats';
                fixed++;
            }
        });

        console.log(`✅ Fixed ${fixed} toggle states`);
        return fixed;
    }
};

// Make ToggleHandler available globally
window.ToggleHandler = ToggleHandler;