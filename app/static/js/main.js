// app/static/js/main.js
// Main JavaScript for Clash Finder

(function() {
    'use strict';

    // Initialize on DOM ready
    document.addEventListener('DOMContentLoaded', function() {
        initFlashMessages();
        initDropdowns();
        initTabs();
        initModals();
        initTooltips();
        initFormValidation();
    });

    /**
     * Flash Messages Auto-hide
     */
    function initFlashMessages() {
        const flashMessages = document.querySelectorAll('.flash-message');

        flashMessages.forEach(function(message) {
            // Auto-hide after 5 seconds
            setTimeout(function() {
                fadeOut(message);
            }, 5000);
        });
    }

    /**
     * Dropdown Functionality
     */
    function initDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown');

        dropdowns.forEach(function(dropdown) {
            const toggle = dropdown.querySelector('.dropdown-toggle');

            if (toggle) {
                toggle.addEventListener('click', function(e) {
                    e.stopPropagation();

                    // Close other dropdowns
                    dropdowns.forEach(function(d) {
                        if (d !== dropdown) {
                            d.classList.remove('active');
                        }
                    });

                    // Toggle current dropdown
                    dropdown.classList.toggle('active');
                });
            }
        });

        // Close dropdowns when clicking outside
        document.addEventListener('click', function() {
            dropdowns.forEach(function(dropdown) {
                dropdown.classList.remove('active');
            });
        });
    }

    /**
     * Tab Functionality
     */
    function initTabs() {
        const tabs = document.querySelectorAll('.tab');

        tabs.forEach(function(tab) {
            tab.addEventListener('click', function() {
                const targetId = this.getAttribute('data-tab');

                if (!targetId) return;

                // Remove active class from all tabs
                tabs.forEach(function(t) {
                    t.classList.remove('active');
                });

                // Add active class to clicked tab
                this.classList.add('active');

                // Hide all tab contents
                const tabContents = document.querySelectorAll('.tab-content');
                tabContents.forEach(function(content) {
                    content.classList.remove('active');
                });

                // Show target tab content
                const targetContent = document.getElementById(targetId);
                if (targetContent) {
                    targetContent.classList.add('active');
                }
            });
        });
    }

    /**
     * Modal Functionality
     */
    function initModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');

        modalTriggers.forEach(function(trigger) {
            trigger.addEventListener('click', function(e) {
                e.preventDefault();
                const modalId = this.getAttribute('data-modal');
                const modal = document.getElementById(modalId);

                if (modal) {
                    openModal(modal);
                }
            });
        });

        // Close buttons
        const closeButtons = document.querySelectorAll('.modal-close');
        closeButtons.forEach(function(btn) {
            btn.addEventListener('click', function() {
                const modal = this.closest('.modal');
                if (modal) {
                    closeModal(modal);
                }
            });
        });

        // Close on overlay click
        const modals = document.querySelectorAll('.modal');
        modals.forEach(function(modal) {
            modal.addEventListener('click', function(e) {
                if (e.target === this) {
                    closeModal(this);
                }
            });
        });

        // Close on Escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                const activeModal = document.querySelector('.modal.active');
                if (activeModal) {
                    closeModal(activeModal);
                }
            }
        });
    }

    /**
     * Tooltip Functionality
     */
    function initTooltips() {
        // Tooltips are handled by CSS
        // This is a placeholder for any JS-based tooltip enhancements
    }

    /**
     * Form Validation
     */
    function initFormValidation() {
        const forms = document.querySelectorAll('.needs-validation');

        forms.forEach(function(form) {
            form.addEventListener('submit', function(e) {
                if (!form.checkValidity()) {
                    e.preventDefault();
                    e.stopPropagation();
                }

                form.classList.add('was-validated');
            });
        });
    }

    /**
     * Helper Functions
     */

    function fadeOut(element, callback) {
        element.style.transition = 'opacity 0.3s';
        element.style.opacity = '0';

        setTimeout(function() {
            element.style.display = 'none';
            if (callback) callback();
        }, 300);
    }

    function fadeIn(element) {
        element.style.display = '';
        element.style.opacity = '0';

        setTimeout(function() {
            element.style.transition = 'opacity 0.3s';
            element.style.opacity = '1';
        }, 10);
    }

    function openModal(modal) {
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal(modal) {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    /**
     * API Helper Functions
     */
    window.ClashFinder = {
        /**
         * Make API request
         */
        apiRequest: function(url, options) {
            options = options || {};

            const defaultOptions = {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                }
            };

            const finalOptions = Object.assign({}, defaultOptions, options);

            return fetch(url, finalOptions)
                .then(function(response) {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .catch(function(error) {
                    console.error('API request failed:', error);
                    throw error;
                });
        },

        /**
         * Show loading indicator
         */
        showLoading: function(element) {
            if (typeof element === 'string') {
                element = document.querySelector(element);
            }

            if (element) {
                element.classList.add('loading');
            }
        },

        /**
         * Hide loading indicator
         */
        hideLoading: function(element) {
            if (typeof element === 'string') {
                element = document.querySelector(element);
            }

            if (element) {
                element.classList.remove('loading');
            }
        },

        /**
         * Show notification
         */
        notify: function(message, type) {
            type = type || 'info';

            const notification = document.createElement('div');
            notification.className = 'flash-message flash-' + type;
            notification.innerHTML = `
                <span class="flash-text">${message}</span>
                <button class="flash-close">×</button>
            `;

            const container = document.querySelector('.flash-messages') || createFlashContainer();
            container.appendChild(notification);

            // Add close handler
            notification.querySelector('.flash-close').addEventListener('click', function() {
                fadeOut(notification, function() {
                    notification.remove();
                });
            });

            // Auto-hide after 5 seconds
            setTimeout(function() {
                fadeOut(notification, function() {
                    notification.remove();
                });
            }, 5000);
        },

        /**
         * Debounce function
         */
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = function() {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },

        /**
         * Throttle function
         */
        throttle: function(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(function() {
                        inThrottle = false;
                    }, limit);
                }
            };
        }
    };

    /**
     * Private helper to create flash container
     */
    function createFlashContainer() {
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
        return container;
    }

    /**
     * Smooth scroll to element
     */
    window.scrollToElement = function(element, offset) {
        offset = offset || 0;

        if (typeof element === 'string') {
            element = document.querySelector(element);
        }

        if (element) {
            const elementPosition = element.getBoundingClientRect().top + window.pageYOffset;
            const offsetPosition = elementPosition - offset;

            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    };

    /**
     * Copy to clipboard
     */
    window.copyToClipboard = function(text) {
        if (navigator.clipboard) {
            navigator.clipboard.writeText(text).then(function() {
                window.ClashFinder.notify('Skopiowano do schowka!', 'success');
            }).catch(function(err) {
                console.error('Failed to copy:', err);
                window.ClashFinder.notify('Błąd kopiowania', 'error');
            });
        } else {
            // Fallback for older browsers
            const textarea = document.createElement('textarea');
            textarea.value = text;
            textarea.style.position = 'fixed';
            textarea.style.opacity = '0';
            document.body.appendChild(textarea);
            textarea.select();

            try {
                document.execCommand('copy');
                window.ClashFinder.notify('Skopiowano do schowka!', 'success');
            } catch (err) {
                console.error('Failed to copy:', err);
                window.ClashFinder.notify('Błąd kopiowania', 'error');
            }

            document.body.removeChild(textarea);
        }
    };

})();