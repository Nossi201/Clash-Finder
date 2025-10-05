// app/static/js/modules/toggle-handler.js
// Handle view toggles and switches

(function(window) {
    'use strict';

    /**
     * Toggle Handler
     */
    const ToggleHandler = {
        /**
         * Initialize toggle functionality
         */
        init: function(selector, options) {
            options = options || {};
            const defaultOptions = {
                activeClass: 'active',
                storageKey: null,
                onToggle: null
            };

            const config = Object.assign({}, defaultOptions, options);
            const toggles = document.querySelectorAll(selector);

            toggles.forEach(function(toggle) {
                toggle.addEventListener('click', function() {
                    const target = this.getAttribute('data-toggle');
                    const group = this.getAttribute('data-toggle-group');

                    if (group) {
                        // Radio-style toggle (only one active)
                        ToggleHandler.radioToggle(selector, this, config);
                    } else {
                        // Checkbox-style toggle (multiple can be active)
                        ToggleHandler.checkboxToggle(this, config);
                    }

                    // Callback
                    if (config.onToggle) {
                        config.onToggle(this, target);
                    }

                    // Save to localStorage
                    if (config.storageKey) {
                        ToggleHandler.saveState(config.storageKey, this);
                    }
                });
            });

            // Load saved state
            if (config.storageKey) {
                ToggleHandler.loadState(config.storageKey, selector, config);
            }
        },

        /**
         * Radio-style toggle
         */
        radioToggle: function(selector, activeElement, config) {
            const allToggles = document.querySelectorAll(selector);
            const group = activeElement.getAttribute('data-toggle-group');

            // Remove active class from all in group
            allToggles.forEach(function(toggle) {
                if (toggle.getAttribute('data-toggle-group') === group) {
                    toggle.classList.remove(config.activeClass);
                }
            });

            // Add active class to clicked element
            activeElement.classList.add(config.activeClass);
        },

        /**
         * Checkbox-style toggle
         */
        checkboxToggle: function(element, config) {
            element.classList.toggle(config.activeClass);
        },

        /**
         * Save toggle state to localStorage
         */
        saveState: function(key, element) {
            const state = {
                target: element.getAttribute('data-toggle'),
                group: element.getAttribute('data-toggle-group')
            };

            try {
                localStorage.setItem(key, JSON.stringify(state));
            } catch (e) {
                console.warn('Failed to save toggle state:', e);
            }
        },

        /**
         * Load toggle state from localStorage
         */
        loadState: function(key, selector, config) {
            try {
                const savedState = localStorage.getItem(key);

                if (savedState) {
                    const state = JSON.parse(savedState);
                    const toggles = document.querySelectorAll(selector);

                    toggles.forEach(function(toggle) {
                        const target = toggle.getAttribute('data-toggle');
                        const group = toggle.getAttribute('data-toggle-group');

                        if (target === state.target && group === state.group) {
                            toggle.click();
                        }
                    });
                }
            } catch (e) {
                console.warn('Failed to load toggle state:', e);
            }
        },

        /**
         * Toggle element visibility
         */
        toggleVisibility: function(element, show) {
            if (typeof element === 'string') {
                element = document.querySelector(element);
            }

            if (!element) return;

            if (show === undefined) {
                // Toggle
                element.classList.toggle('hidden');
            } else {
                // Set explicit state
                if (show) {
                    element.classList.remove('hidden');
                } else {
                    element.classList.add('hidden');
                }
            }
        },

        /**
         * Toggle class on element
         */
        toggleClass: function(element, className) {
            if (typeof element === 'string') {
                element = document.querySelector(element);
            }

            if (element) {
                element.classList.toggle(className);
            }
        }
    };

    // Export to window
    window.ToggleHandler = ToggleHandler;

})(window);