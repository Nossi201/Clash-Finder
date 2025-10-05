// app/static/js/player_history.js
/**
 * Player History JavaScript
 * Handles match loading and interactions
 */

(function() {
    'use strict';

    console.log('Player history script loaded');

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', function() {
        console.log('Player history page ready');
        initLoadMore();
    });

    /**
     * Initialize "Load More" button
     */
    function initLoadMore() {
        const loadMoreBtn = document.getElementById('load-more-btn');

        if (!loadMoreBtn) {
            console.log('Load more button not found - end of matches');
            return;
        }

        console.log('Load more button initialized');

        loadMoreBtn.addEventListener('click', function(e) {
            e.preventDefault();
            loadMoreMatches();
        });
    }

    /**
     * Load more matches via AJAX
     */
    function loadMoreMatches() {
        console.log('Loading more matches...');

        const loadMoreBtn = document.getElementById('load-more-btn');
        const btnText = loadMoreBtn.querySelector('.btn-text');
        const btnLoader = loadMoreBtn.querySelector('.btn-loader');
        const playerData = document.getElementById('player-data');

        if (!playerData) {
            console.error('Player data element not found');
            alert('Błąd: Brak danych gracza');
            return;
        }

        // Get player info
        const summonerName = playerData.dataset.summonerName;
        const summonerTag = playerData.dataset.summonerTag;
        const server = playerData.dataset.server;
        const currentCount = parseInt(playerData.dataset.currentCount) || 0;

        console.log('Player:', summonerName + '#' + summonerTag);
        console.log('Current count:', currentCount);

        // Show loading state
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
        loadMoreBtn.disabled = true;

        // Make AJAX request
        fetch('/player_stats/load_more', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                SUMMONER_NAME: summonerName,
                SUMMONER_TAG: summonerTag,
                server: server,
                current_count: currentCount,
                number: 5
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error('HTTP error ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Received data:', data);

            if (data && data.length > 0) {
                // Update count
                const newCount = currentCount + data.length;
                playerData.dataset.currentCount = newCount;

                console.log('Reloading page to show new matches...');
                // Reload page to show new matches
                location.reload();
            } else {
                console.log('No more matches');
                alert('Brak więcej meczów do wyświetlenia');
                loadMoreBtn.style.display = 'none';
            }
        })
        .catch(error => {
            console.error('Error loading matches:', error);
            alert('Błąd podczas ładowania meczów: ' + error.message);
        })
        .finally(() => {
            // Hide loading state
            btnText.style.display = 'inline';
            btnLoader.style.display = 'none';
            loadMoreBtn.disabled = false;
        });
    }

})();