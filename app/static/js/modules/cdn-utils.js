// app/static/js/cdn-utils.js
// Utility for Data Dragon CDN URLs

const CDNUtils = {
    getVersion: function() {
        // Try to get version from context processor in template
        const versionMeta = document.querySelector('meta[name="ddragon-version"]');
        if (versionMeta) {
            return versionMeta.content;
        }

        // Fallback to data attribute
        const versionEl = document.querySelector('[data-ddragon-version]');
        if (versionEl) {
            return versionEl.dataset.ddragonVersion;
        }

        // Last resort fallback
        return '15.19.1';
    },

    BASE_URL: 'https://ddragon.leagueoflegends.com/cdn',

    getChampionIconUrl: function(championName) {
        const version = this.getVersion();
        return `${this.BASE_URL}/${version}/img/champion/${championName}.png`;
    },

    getItemIconUrl: function(itemId) {
        const version = this.getVersion();
        return `${this.BASE_URL}/${version}/img/item/${itemId}.png`;
    },

    getSpellIconUrl: function(spellName) {
        const version = this.getVersion();
        return `${this.BASE_URL}/${version}/img/spell/${spellName}.png`;
    },

    getProfileIconUrl: function(iconId) {
        const version = this.getVersion();
        return `${this.BASE_URL}/${version}/img/profileicon/${iconId}.png`;
    }
};

// Make globally available
window.CDNUtils = CDNUtils;