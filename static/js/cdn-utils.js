// static/js/cdn-utils.js
// Simplified CDN utilities module - direct CDN access

console.log('📦 CDN Utils module loaded');

// Champion name fixes for special cases (zgodne z cdn_config.py)
const championNameFixes = {
    "Fiddlesticks": "FiddleSticks",
    "Wukong": "MonkeyKing",
    "RekSai": "RekSai",
    "Renata Glasc": "Renata",
    "Nunu & Willump": "Nunu",
    "Kai'Sa": "Kaisa",
    "Kha'Zix": "Khazix",
    "Vel'Koz": "Velkoz",
    "Cho'Gath": "Chogath",
    "Kog'Maw": "KogMaw",
    "LeBlanc": "Leblanc",
    "Bel'Veth": "Belveth"
};

const CDNUtils = {
    // Base CDN URL - taki sam jak w cdn_config.py
    baseCDNUrl: 'https://ddragon.leagueoflegends.com',

    // Current version (fallback, ale lepiej pobrać dynamicznie)
    currentVersion: '15.15.1',

    // Champion name fixing
    fixChampionName(championName) {
        const fixed = championNameFixes[championName] || championName;
        if (fixed !== championName) {
            console.log(`🔧 Champion name fixed: '${championName}' -> '${fixed}'`);
        }
        return fixed;
    },

    // Get current version from Riot API
    async getCurrentVersion() {
        try {
            const response = await fetch('https://ddragon.leagueoflegends.com/api/versions.json');
            const versions = await response.json();
            this.currentVersion = versions[0];
            console.log('✅ Version fetched:', this.currentVersion);
            return this.currentVersion;
        } catch (error) {
            console.warn('⚠️ Failed to fetch version, using fallback:', error);
            return this.currentVersion;
        }
    },

    // Direct URL generators - takie same jak w cdn_config.py
    async getChampionImageUrl(championName) {
        const fixedName = this.fixChampionName(championName);
        await this.getCurrentVersion(); // Refresh version if needed
        return `${this.baseCDNUrl}/cdn/${this.currentVersion}/img/champion/${fixedName}.png`;
    },

    async getItemImageUrl(itemId) {
        if (itemId === 0) return '';
        await this.getCurrentVersion();
        return `${this.baseCDNUrl}/cdn/${this.currentVersion}/img/item/${itemId}.png`;
    },

    async getSummonerSpellImageUrl(spellId) {
        // Fallback mapping - w produkcji lepiej pobrać z API
        const spellMapping = {
            1: 'SummonerBoost.png',
            3: 'SummonerExhaust.png',
            4: 'SummonerFlash.png',
            6: 'SummonerHaste.png',
            7: 'SummonerHeal.png',
            11: 'SummonerSmite.png',
            12: 'SummonerTeleport.png',
            13: 'SummonerMana.png',
            14: 'SummonerDot.png',
            21: 'SummonerBarrier.png'
        };

        const fileName = spellMapping[spellId] || 'SummonerFlash.png';
        await this.getCurrentVersion();
        return `${this.baseCDNUrl}/cdn/${this.currentVersion}/img/spell/${fileName}`;
    },

    async getRuneImageUrl(runeId) {
        // Dla run potrzebujemy manifest - to jest uproszczenie
        // W produkcji lepiej cache'ować manifesty lub używać cdn_config.py endpointów
        await this.getCurrentVersion();
        return `${this.baseCDNUrl}/cdn/${this.currentVersion}/img/perk-images/Styles/RunesIcon.png`;
    },

    async getRuneStyleImageUrl(styleId) {
        // Mapping stylów run
        const styleMapping = {
            8000: 'perk-images/Styles/7200_Precision.png',
            8100: 'perk-images/Styles/7201_Domination.png',
            8200: 'perk-images/Styles/7202_Sorcery.png',
            8300: 'perk-images/Styles/7203_Whimsy.png',
            8400: 'perk-images/Styles/7204_Resolve.png'
        };

        const iconPath = styleMapping[styleId];
        if (iconPath) {
            await this.getCurrentVersion();
            return `${this.baseCDNUrl}/cdn/${this.currentVersion}/img/${iconPath}`;
        }
        return '';
    },

    // Helper to create image elements with error handling
    async createImageElement(urlPromise, alt, className, errorHandler = 'hide') {
        const url = await urlPromise;
        if (!url) {
            if (errorHandler === 'empty-slot') {
                return `<div class="${className} empty-slot"></div>`;
            }
            return '';
        }

        const onError = errorHandler === 'empty-slot'
            ? `onerror="this.classList.add('empty-slot'); this.src='';"`
            : `onerror="this.style.display='none'"`;

        return `<img src="${url}" alt="${alt}" class="${className}" ${onError}>`;
    },

    // Initialize - much simpler now
    async initialize() {
        console.log('🔄 Initializing CDN utils...');
        try {
            await this.getCurrentVersion();
            console.log('✅ CDN utils initialized');
            return true;
        } catch (error) {
            console.warn('⚠️ CDN initialization failed:', error);
            return false;
        }
    },

    // Debug helper
    async testUrls() {
        console.log('🧪 Testing CDN URLs...');

        const championUrl = await this.getChampionImageUrl('Aatrox');
        const itemUrl = await this.getItemImageUrl(1001);
        const spellUrl = await this.getSummonerSpellImageUrl(4);

        console.log('🏆 Champion URL:', championUrl);
        console.log('🛡️ Item URL:', itemUrl);
        console.log('✨ Spell URL:', spellUrl);

        return {
            champion: championUrl,
            item: itemUrl,
            spell: spellUrl
        };
    }
};

// Make CDNUtils available globally
window.CDNUtils = CDNUtils;

// Auto-initialize when loaded
document.addEventListener('DOMContentLoaded', function() {
    CDNUtils.initialize();
});