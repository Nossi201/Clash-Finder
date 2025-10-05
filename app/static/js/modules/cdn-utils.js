// app/static/js/modules/cdn-utils.js
// CDN and resource URL utilities

(function(window) {
    'use strict';

    const CDN_CONFIG = {
        BASE_URL: 'https://ddragon.leagueoflegends.com/cdn',
        VERSION: '14.1.1',
        COMMUNITY_DRAGON: 'https://raw.communitydragon.org/latest'
    };

    /**
     * CDN Utilities
     */
    const CDNUtils = {
        /**
         * Get champion icon URL
         */
        getChampionIcon: function(championName) {
            return `${CDN_CONFIG.BASE_URL}/${CDN_CONFIG.VERSION}/img/champion/${championName}.png`;
        },

        /**
         * Get champion splash URL
         */
        getChampionSplash: function(championKey, skinNum) {
            skinNum = skinNum || 0;
            return `${CDN_CONFIG.BASE_URL}/img/champion/splash/${championKey}_${skinNum}.jpg`;
        },

        /**
         * Get item icon URL
         */
        getItemIcon: function(itemId) {
            return `${CDN_CONFIG.BASE_URL}/${CDN_CONFIG.VERSION}/img/item/${itemId}.png`;
        },

        /**
         * Get summoner spell icon URL
         */
        getSpellIcon: function(spellName) {
            return `${CDN_CONFIG.BASE_URL}/${CDN_CONFIG.VERSION}/img/spell/${spellName}.png`;
        },

        /**
         * Get profile icon URL
         */
        getProfileIcon: function(iconId) {
            return `${CDN_CONFIG.BASE_URL}/${CDN_CONFIG.VERSION}/img/profileicon/${iconId}.png`;
        },

        /**
         * Get rune icon URL
         */
        getRuneIcon: function(runeId) {
            return `${CDN_CONFIG.COMMUNITY_DRAGON}/plugins/rcp-be-lol-game-data/global/default/v1/perk-images/styles/${runeId}.png`;
        },

        /**
         * Preload image
         */
        preloadImage: function(url) {
            return new Promise(function(resolve, reject) {
                const img = new Image();
                img.onload = function() { resolve(img); };
                img.onerror = function() { reject(new Error('Failed to load image: ' + url)); };
                img.src = url;
            });
        },

        /**
         * Preload multiple images
         */
        preloadImages: function(urls) {
            const promises = urls.map(function(url) {
                return CDNUtils.preloadImage(url);
            });
            return Promise.all(promises);
        },

        /**
         * Get spell ID to name mapping
         */
        getSpellName: function(spellId) {
            const spellMap = {
                1: 'SummonerBoost',
                3: 'SummonerExhaust',
                4: 'SummonerFlash',
                6: 'SummonerHaste',
                7: 'SummonerHeal',
                11: 'SummonerSmite',
                12: 'SummonerTeleport',
                13: 'SummonerMana',
                14: 'SummonerDot',
                21: 'SummonerBarrier',
                32: 'SummonerSnowball'
            };
            return spellMap[spellId] || 'SummonerBlank';
        },

        /**
         * Set CDN version
         */
        setVersion: function(version) {
            CDN_CONFIG.VERSION = version;
        },

        /**
         * Get current CDN version
         */
        getVersion: function() {
            return CDN_CONFIG.VERSION;
        }
    };

    // Export to window
    window.CDNUtils = CDNUtils;

})(window);