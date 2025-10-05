// app/static/js/modules/match-renderer.js
// Render match cards dynamically

(function(window) {
    'use strict';

    /**
     * Match Renderer
     */
    const MatchRenderer = {
        /**
         * Render a single match card
         */
        renderMatch: function(match, options) {
            options = options || {};

            const card = document.createElement('div');
            card.className = 'match-card ' + (match.win ? 'match-win' : 'match-loss');

            card.innerHTML = MatchRenderer.generateMatchHTML(match, options);

            return card;
        },

        /**
         * Generate match HTML
         */
        generateMatchHTML: function(match, options) {
            const stats = MatchRenderer.calculateStats(match);

            return `
                <div class="match-result-banner">
                    <span class="result-text">${match.win ? 'WYGRANA' : 'PRZEGRANA'}</span>
                    <span class="result-duration">${stats.duration}</span>
                </div>

                <div class="match-header">
                    <div class="match-info">
                        <span class="queue-type">${stats.queueName}</span>
                        <span class="match-date">${stats.timeAgo}</span>
                    </div>
                </div>

                <div class="match-body">
                    ${MatchRenderer.generateChampionSection(match)}
                    ${MatchRenderer.generateStatsSection(stats)}
                    ${MatchRenderer.generateItemsSection(match)}
                </div>
            `;
        },

        /**
         * Generate champion section
         */
        generateChampionSection: function(match) {
            return `
                <div class="champion-section">
                    <div class="champion-icon">
                        <img src="${window.CDNUtils ? window.CDNUtils.getChampionIcon(match.championName) : ''}"
                             alt="${match.championName}"
                             onerror="this.src='https://ddragon.leagueoflegends.com/cdn/14.1.1/img/champion/Unknown.png'">
                        <span class="champion-level">${match.champLevel || 1}</span>
                    </div>
                    <div class="champion-info">
                        <h3 class="champion-name">${match.championName}</h3>
                        <div class="summoner-spells">
                            ${MatchRenderer.generateSpellIcons(match)}
                        </div>
                    </div>
                </div>
            `;
        },

        /**
         * Generate spell icons
         */
        generateSpellIcons: function(match) {
            const spell1 = window.CDNUtils ?
                window.CDNUtils.getSpellName(match.summoner1Id) : 'SummonerBlank';
            const spell2 = window.CDNUtils ?
                window.CDNUtils.getSpellName(match.summoner2Id) : 'SummonerBlank';

            return `
                <img src="https://ddragon.leagueoflegends.com/cdn/14.1.1/img/spell/${spell1}.png"
                     alt="Spell 1" class="spell-icon">
                <img src="https://ddragon.leagueoflegends.com/cdn/14.1.1/img/spell/${spell2}.png"
                     alt="Spell 2" class="spell-icon">
            `;
        },

        /**
         * Generate stats section
         */
        generateStatsSection: function(stats) {
            return `
                <div class="stats-basic">
                    <div class="stat-box">
                        <span class="stat-label">KDA</span>
                        <span class="stat-value kda-value">${stats.kdaFormatted}</span>
                        <span class="stat-ratio">${stats.kdaRatio} KDA</span>
                    </div>

                    <div class="stat-box">
                        <span class="stat-label">CS</span>
                        <span class="stat-value">${stats.cs}</span>
                        <span class="stat-ratio">${stats.csPerMin}/min</span>
                    </div>

                    <div class="stat-box">
                        <span class="stat-label">Złoto</span>
                        <span class="stat-value">${stats.gold}</span>
                    </div>
                </div>
            `;
        },

        /**
         * Generate items section
         */
        generateItemsSection: function(match) {
            let html = '<div class="items-section">';

            for (let i = 0; i < 7; i++) {
                const itemId = match['item' + i] || 0;

                if (itemId > 0) {
                    html += `
                        <div class="item-slot">
                            <img src="https://ddragon.leagueoflegends.com/cdn/14.1.1/img/item/${itemId}.png"
                                 alt="Item ${itemId}" class="item-icon">
                        </div>
                    `;
                } else {
                    html += '<div class="item-slot"><div class="item-empty"></div></div>';
                }
            }

            html += '</div>';
            return html;
        },

        /**
         * Calculate match statistics
         */
        calculateStats: function(match) {
            const kills = match.kills || 0;
            const deaths = match.deaths || 0;
            const assists = match.assists || 0;
            const cs = (match.totalMinionsKilled || 0) + (match.neutralMinionsKilled || 0);
            const duration = match.gameDuration || 0;

            const kdaRatio = deaths === 0 ?
                (kills + assists).toFixed(2) :
                ((kills + assists) / deaths).toFixed(2);

            const csPerMin = duration > 0 ?
                (cs / (duration / 60)).toFixed(1) : '0.0';

            return {
                kdaFormatted: `${kills}/${deaths}/${assists}`,
                kdaRatio: kdaRatio,
                cs: cs,
                csPerMin: csPerMin,
                gold: MatchRenderer.formatGold(match.goldEarned || 0),
                duration: MatchRenderer.formatDuration(duration),
                queueName: MatchRenderer.getQueueName(match.queueId),
                timeAgo: MatchRenderer.formatTimeAgo(match.gameCreation)
            };
        },

        /**
         * Format duration
         */
        formatDuration: function(seconds) {
            const minutes = Math.floor(seconds / 60);
            const secs = seconds % 60;
            return `${minutes}:${secs.toString().padStart(2, '0')}`;
        },

        /**
         * Format gold
         */
        formatGold: function(gold) {
            if (gold >= 1000) {
                return (gold / 1000).toFixed(1) + 'k';
            }
            return gold.toString();
        },

        /**
         * Format time ago
         */
        formatTimeAgo: function(timestamp) {
            if (!timestamp) return 'N/A';

            const date = new Date(timestamp);
            const now = new Date();
            const diff = now - date;

            const minutes = Math.floor(diff / 60000);
            const hours = Math.floor(diff / 3600000);
            const days = Math.floor(diff / 86400000);

            if (minutes < 60) {
                return `${minutes} min temu`;
            } else if (hours < 24) {
                return `${hours} godz. temu`;
            } else if (days < 7) {
                return `${days} dni temu`;
            } else {
                return date.toLocaleDateString('pl-PL');
            }
        },

        /**
         * Get queue name
         */
        getQueueName: function(queueId) {
            const queueNames = {
                420: 'Ranked Solo/Duo',
                440: 'Ranked Flex',
                400: 'Normal Draft',
                430: 'Normal Blind',
                450: 'ARAM',
                700: 'Clash',
                490: 'Normal Quickplay'
            };

            return queueNames[queueId] || `Queue ${queueId}`;
        },

        /**
         * Render multiple matches
         */
        renderMatches: function(matches, container) {
            if (typeof container === 'string') {
                container = document.querySelector(container);
            }

            if (!container) {
                console.error('Container not found');
                return;
            }

            matches.forEach(function(match) {
                const card = MatchRenderer.renderMatch(match);
                container.appendChild(card);

                // Add animation
                setTimeout(function() {
                    card.classList.add('fade-in');
                }, 10);
            });
        }
    };

    // Export to window
    window.MatchRenderer = MatchRenderer;

})(window);