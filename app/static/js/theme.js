// app/static/js/theme.js
/**
 * Theme Management
 * Handles dark/light mode switching
 */

(function() {
    'use strict';

    // Theme toggle functionality
    const themeToggle = document.getElementById('theme-toggle');
    const html = document.documentElement;

    if (!themeToggle) {
        console.warn('Theme toggle button not found');
        return;
    }

    const themeIcon = themeToggle.querySelector('.theme-icon');

    /**
     * Get initial theme
     */
    function getInitialTheme() {
        // Check localStorage first
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme) {
            return savedTheme;
        }

        // Check system preference
        const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        return systemPrefersDark ? 'dark' : 'light';
    }

    /**
     * Apply theme
     */
    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
        localStorage.setItem('theme', theme);

        console.log(`Theme applied: ${theme}`);
    }

    /**
     * Toggle theme
     */
    function toggleTheme() {
        const currentTheme = html.getAttribute('data-theme');
        const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
        applyTheme(newTheme);
    }

    // Initialize theme
    const initialTheme = getInitialTheme();
    applyTheme(initialTheme);

    // Add click listener
    themeToggle.addEventListener('click', toggleTheme);

    // Listen for system theme changes
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
        // Only auto-switch if user hasn't manually set a preference
        if (!localStorage.getItem('theme')) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });

    console.log('Theme system initialized');

})();