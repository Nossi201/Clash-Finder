# question.py
import datetime
import pprint

import requests

# A dictionary mapping server names to their regions and domains
servers_to_region = {
    'brazil': ['br1', 'americas', 'br'],
    'latin america north': ['la1', 'americas', 'lan'],
    'latin america south': ['la2', 'americas', 'las'],
    'north america': ['na1', 'americas', 'na'],
    'japan': ['jp1', 'asia', 'jp'],
    'korea': ['kr', 'asia', 'kr'],
    'philippines': ['ph2', 'asia', 'ph'],
    'singapore': ['sg2', 'asia', 'sg'],
    'thailand': ['th2', 'asia', 'th'],
    'taiwan': ['tw2', 'asia', 'tw'],
    'vietnam': ['vn2', 'asia', 'vn'],
    'eu nordic & east': ['eun1', 'europe', 'eune'],
    'eu west': ['euw1', 'europe', 'euw'],
    'russia': ['ru', 'europe', 'ru'],
    'turkey': ['tr1', 'europe', 'tr']
}

API_KEY = "RGAPI-070f4fb3-e23a-4bb7-9a25-95524f7113a9"
HEADERS = {"X-Riot-Token": API_KEY}
RUNES_AND_SHARDS = {
    8100: 'Domination', 8300: 'Inspiration', 8000: 'Precision', 8400: 'Resolve', 8200: 'Sorcery',

    8126: 'CheapShot', 8139: 'TasteOfBlood', 8143: 'SuddenImpact', 8136: 'ZombieWard',
    8120: 'GhostPoro', 8138: 'EyeballCollection', 8135: 'TreasureHunter', 8134: 'IngeniousHunter',
    8105: 'RelentlessHunter', 8106: 'UltimateHunter', 8351: 'GlacialAugment', 8360: 'UnsealedSpellbook',
    8369: 'FirstStrike', 8306: 'HextechFlashtraption', 8304: 'MagicalFootwear', 8313: 'PerfectTiming',
    8321: 'FuturesMarket', 8316: 'MinionDematerializer', 8345: 'BiscuitDelivery', 8347: 'CosmicInsight',
    8410: 'ApproachVelocity', 8352: 'TimeWarpTonic', 8005: 'PressTheAttack', 8008: 'LethalTempo',
    8021: 'FleetFootwork', 8010: 'Conqueror', 9101: 'Overheal', 9111: 'Triumph', 8009: 'PresenceOfMind',
    9104: 'LegendAlacrity', 9105: 'LegendTenacity', 9103: 'LegendBloodline', 8014: 'CoupDeGrace',
    8017: 'CutDown', 8299: 'LastStand', 8437: 'GraspOfTheUndying', 8439: 'Aftershock', 8465: 'Guardian',
    8446: 'Demolish', 8463: 'FontOfLife', 8401: 'ShieldBash', 8429: 'Conditioning', 8444: 'SecondWind',
    8473: 'BonePlating', 8451: 'Overgrowth', 8453: 'Revitalize', 8242: 'Unflinching', 8214: 'SummonAery',
    8229: 'ArcaneComet', 8230: 'PhaseRush', 8224: 'NullifyingOrb', 8226: 'ManaflowBand', 8275: 'NimbusCloak',
    8210: 'Transcendence', 8234: 'Celerity', 8233: 'AbsoluteFocus', 8237: 'Scorch', 8232: 'Waterwalking',
    8236: 'GatheringStorm',
    # Shards
    5001: "Health Scaling",
    5002: "Armor",
    5003: "Magic Resist",
    5005: "Attack Speed",
    5007: "Ability Haste",
    5008: "Adaptive Force",
    5010: "Move Speed",
    5011: "Health",
    5012: "Armor",
    5013: "Magic Resist"
}
ITEMS = {
    0: '',
    222503: 'Blackfire Torch',

    2508: 'Fated Ashes',
    447111: 'Overlord\'s Bloodmail',
    2501: 'Overlord\'s Bloodmail',
    3010: 'Symbiotic Soles',

    3013: 'Synchronized Souls',
    3032: 'Yun Tal Wildarrows',
    223032: 'Yun Tal Wildarrows',
    3144: 'Scout\'s Slingshot',

    1001: 'Boots',
    1004: 'Faerie Charm',
    1006: 'Rejuvenation Bead',
    1011: 'Giant\'s Belt',
    1018: 'Cloak of Agility',
    1026: 'Blasting Wand',
    1027: 'Sapphire Crystal',
    1028: 'Ruby Crystal',
    1029: 'Cloth Armor',
    1031: 'Chain Vest',
    1033: 'Null-Magic Mantle',
    1035: 'Emberknife',
    1036: 'Long Sword',
    1037: 'Pickaxe',
    1038: 'B. F. Sword',
    1039: 'Hailblade',
    1040: 'Obsidian Edge',
    1042: 'Dagger',
    1043: 'Recurve Bow',
    1052: 'Amplifying Tome',
    1053: 'Vampiric Scepter',
    1054: 'Doran\'s Shield',
    1055: 'Doran\'s Blade',
    1056: 'Doran\'s Ring',
    1057: 'Negatron Cloak',
    1058: 'Needlessly Large Rod',
    1082: 'Dark Seal',
    1083: 'Cull',
    1101: 'Scorchclaw Pup',
    1102: 'Gustwalker Hatchling',
    1103: 'Mosstomper Seedling',
    1104: 'Eye of the Herald',
    1500: 'Penetrating Bullets',
    1501: 'Fortification',
    1502: 'Reinforced Armor',
    1503: 'Warden\'s Eye',
    1504: 'Vanguard',
    1506: 'Reinforced Armor',
    1507: 'Overcharged',
    1508: 'Anti-tower Socks',
    1509: 'Gusto',
    1510: 'Phreakish Gusto',
    1511: 'Super Mech Armor',
    1512: 'Super Mech Power Field',
    1515: 'Turret Plating',
    1516: 'Structure Bounty',
    1517: 'Structure Bounty',
    1518: 'Structure Bounty',
    1519: 'Structure Bounty',
    1520: 'OvererchargedHA',
    1521: 'Fortification',
    1522: 'Tower Power-Up',
    2003: 'Health Potion',
    2010: 'Total Biscuit of Everlasting Will',
    2015: 'Kircheis Shard',
    2019: 'Steel Sigil',
    2020: 'The Brutalizer',
    2021: 'Tunneler',
    2022: 'Glowing Mote',
    2031: 'Refillable Potion',
    2033: 'Corrupting Potion',
    2049: 'Guardian\'s Amulet',
    2050: 'Guardian\'s Shroud',
    2051: 'Guardian\'s Horn',
    2052: 'Poro-Snax',
    2055: 'Control Ward',
    2056: 'Stealth Ward',
    2065: 'Shurelya\'s Battlesong',
    2138: 'Elixir of Iron',
    2139: 'Elixir of Sorcery',
    2140: 'Elixir of Wrath',
    2141: 'Cappa Juice',
    2142: 'Juice of Power',
    2143: 'Juice of Vitality',
    2144: 'Juice of Haste',
    2150: 'Elixir of Skill',
    2151: 'Elixir of Avarice',
    2152: 'Elixir of Force',
    221038: 'B. F. Sword',
    221053: 'Vampiric Scepter',
    221058: 'Needlessly Large Rod',
    222051: 'Guardian\'s Horn',
    222065: 'Shurelya\'s Battlesong',
    223001: 'Evenshroud',
    223003: 'Archangel\'s Staff',
    223004: 'Manamune',
    223005: 'Ghostcrawlers',
    223006: 'Berserker\'s Greaves',
    223009: 'Boots of Swiftness',
    223011: 'Chemtech Putrifier',
    223020: 'Sorcerer\'s Shoes',
    223026: 'Guardian Angel',
    223031: 'Infinity Edge',
    223033: 'Mortal Reminder',
    223036: 'Lord Dominik\'s Regards',
    223039: 'Atma\'s Reckoning',
    223040: 'Seraph\'s Embrace',
    223042: 'Muramana',
    223046: 'Phantom Dancer',
    223047: 'Plated Steelcaps',
    223050: 'Zeke\'s Convergence',
    223053: 'Sterak\'s Gage',
    223057: 'Sheen',
    223065: 'Spirit Visage',
    223067: 'Kindlegem',
    223068: 'Sunfire Aegis',
    223071: 'Black Cleaver',
    223072: 'Bloodthirster',
    223074: 'Ravenous Hydra',
    223075: 'Thornmail',
    223078: 'Trinity Force',
    223084: 'Heartsteel',
    223085: 'Runaan\'s Hurricane',
    223087: 'Statikk Shiv',
    223089: 'Rabadon\'s Deathcap',
    223091: 'Wit\'s End',
    223094: 'Rapid Firecannon',
    223095: 'Stormrazor',
    223100: 'Lich Bane',
    223102: 'Banshee\'s Veil',
    223105: 'Aegis of the Legion',
    223107: 'Redemption',
    223109: 'Knight\'s Vow',
    223110: 'Frozen Heart',
    223111: 'Mercury\'s Treads',
    223112: 'Guardian\'s Orb',
    223115: 'Nashor\'s Tooth',
    223116: 'Rylai\'s Crystal Scepter',
    223119: 'Winter\'s Approach',
    223121: 'Fimbulwinter',
    223124: 'Guinsoo\'s Rageblade',
    223135: 'Void Staff',
    223139: 'Mercurial Scimitar',
    223142: 'Youmuu\'s Ghostblade',
    223143: 'Randuin\'s Omen',
    223146: 'Hextech Gunblade',
    223152: 'Hextech Rocketbelt',
    223153: 'Blade of The Ruined King',
    223156: 'Maw of Malmortius',
    223157: 'Zhonya\'s Hourglass',
    223158: 'Ionian Boots of Lucidity',
    223161: 'Spear of Shojin',
    223165: 'Morellonomicon',
    223172: 'Zephyr',
    223177: 'Guardian\'s Blade',
    223181: 'Hullbreaker',
    223184: 'Guardian\'s Hammer',
    223185: 'Guardian\'s Dirk',
    223190: 'Locket of the Iron Solari',
    223193: 'Gargoyle Stoneplate',
    223222: 'Mikael\'s Blessing',
    223504: 'Ardent Censer',
    223508: 'Essence Reaver',
    223742: 'Dead Man\'s Plate',
    223748: 'Titanic Hydra',
    223814: 'Edge of Night',
    224004: 'Spectral Cutlass',
    224005: 'Imperial Mandate',
    224401: 'Force of Nature',
    224403: 'The Golden Spatula',
    224628: 'Horizon Focus',
    224629: 'Cosmic Drive',
    224633: 'Riftmaker',
    224636: 'Night Harvester',
    224637: 'Demonic Embrace',
    224644: 'Crown of the Shattered Queen',
    224645: 'Shadowflame',
    226035: 'Silvermere Dawn',
    226333: 'Death\'s Dance',
    226609: 'Chempunk Chainsword',
    226616: 'Staff of Flowing Water',
    226617: 'Moonstone Renewer',
    226620: 'Echoes of Helia',
    226630: 'Goredrinker',
    226631: 'Stridebreaker',
    226632: 'Divine Sunderer',
    226653: 'Liandry\'s Anguish',
    226655: 'Luden\'s Tempest',
    226656: 'Everfrost',
    226657: 'Rod of Ages',
    226662: 'Iceborn Gauntlet',
    226665: 'Jak\'Sho, The Protean',
    226667: 'Radiant Virtue',
    226671: 'Galeforce',
    226672: 'Kraken Slayer',
    226673: 'Immortal Shieldbow',
    226675: 'Navori Quickblades',
    226676: 'The Collector',
    226691: 'Duskblade of Draktharr',
    226692: 'Eclipse',
    226693: 'Prowler\'s Claw',
    226694: 'Serylda\'s Grudge',
    226695: 'Serpent\'s Fang',
    226696: 'Axiom Arc',
    227001: 'Syzygy',
    227002: 'Draktharr\'s Shadowcarver',
    227005: 'Frozen Fist',
    227006: 'Typhoon',
    227009: 'Icathia\'s Curse',
    227010: 'Vespertide',
    227011: 'Upgraded Aeropack',
    227012: 'Liandry\'s Lament',
    227013: 'Force of Arms',
    227014: 'Eternal Winter',
    227015: 'Ceaseless Hunger',
    227016: 'Dreamshatter',
    227017: 'Deicide',
    227018: 'Infinity Force',
    227019: 'Reliquary of the Golden Dawn',
    227020: 'Shurelya\'s Requiem',
    227021: 'Starcaster',
    227023: 'Equinox',
    227024: 'Caesura',
    227025: 'Leviathan',
    227026: 'The Unspoken Parasite',
    227027: 'Primordial Dawn',
    227028: 'Infinite Convergence',
    227029: 'Youmuu\'s Wake',
    227030: 'Seething Sorrow',
    227031: 'Edge of Finality',
    227032: 'Flicker',
    227033: 'Cry of the Shrieking City',
    228001: 'Anathema\'s Chains',
    228002: 'Wooglet\'s Witchcap',
    228003: 'Deathblade',
    228004: 'Adaptive Helm',
    228005: 'Obsidian Cleaver',
    228006: 'Sanguine Blade',
    228008: 'Runeglaive',
    228020: 'Abyssal Mask',
    2403: 'Minion Dematerializer',
    2419: 'Commencing Stopwatch',
    2420: 'Seeker\'s Armguard',
    2421: 'Shattered Armguard',
    2422: 'Slightly Magical Footwear',
    2423: 'Perfectly Timed Stopwatch',
    2502: 'Unending Despair',
    2504: 'Kaenic Rookern',
    3001: 'Evenshroud',
    3002: 'Trailblazer',
    3003: 'Archangel\'s Staff',
    3004: 'Manamune',
    3005: 'Ghostcrawlers',
    3006: 'Berserker\'s Greaves',
    3009: 'Boots of Swiftness',
    3011: 'Chemtech Putrifier',
    3012: 'Chalice of Blessing',
    3020: 'Sorcerer\'s Shoes',
    3023: 'Lifewell Pendant',
    3024: 'Glacial Buckler',
    3026: 'Guardian Angel',
    3031: 'Infinity Edge',
    3033: 'Mortal Reminder',
    3035: 'Last Whisper',
    3036: 'Lord Dominik\'s Regards',
    3039: 'Atma\'s Reckoning',
    3040: 'Seraph\'s Embrace',
    3041: 'Mejai\'s Soulstealer',
    3042: 'Muramana',
    3044: 'Phage',
    3046: 'Phantom Dancer',
    3047: 'Plated Steelcaps',
    3050: 'Zeke\'s Convergence',
    3051: 'Hearthbound Axe',
    3053: 'Sterak\'s Gage',
    3057: 'Sheen',
    3065: 'Spirit Visage',
    3066: 'Winged Moonplate',
    3067: 'Kindlegem',
    3068: 'Sunfire Aegis',
    3070: 'Tear of the Goddess',
    3071: 'Black Cleaver',
    3072: 'Bloodthirster',
    3073: 'Experimental Hexplate',
    3074: 'Ravenous Hydra',
    3075: 'Thornmail',
    3076: 'Bramble Vest',
    3077: 'Tiamat',
    3078: 'Trinity Force',
    3082: 'Warden\'s Mail',
    3083: 'Warmog\'s Armor',
    3084: 'Heartsteel',
    3085: 'Runaan\'s Hurricane',
    3086: 'Zeal',
    3087: 'Statikk Shiv',
    3089: 'Rabadon\'s Deathcap',
    3091: 'Wit\'s End',
    3094: 'Rapid Firecannon',
    3095: 'Stormrazor',
    3100: 'Lich Bane',
    3102: 'Banshee\'s Veil',
    3105: 'Aegis of the Legion',
    3107: 'Redemption',
    3108: 'Fiendish Codex',
    3109: 'Knight\'s Vow',
    3110: 'Frozen Heart',
    3111: 'Mercury\'s Treads',
    3112: 'Guardian\'s Orb',
    3113: 'Aether Wisp',
    3114: 'Forbidden Idol',
    3115: 'Nashor\'s Tooth',
    3116: 'Rylai\'s Crystal Scepter',
    3117: 'Mobility Boots',
    3118: 'Malignance',
    3119: 'Winter\'s Approach',
    3121: 'Fimbulwinter',
    3123: 'Executioner\'s Calling',
    3124: 'Guinsoo\'s Rageblade',
    3128: 'Deathfire Grasp',
    3131: 'Sword of the Divine',
    3133: 'Caulfield\'s Warhammer',
    3134: 'Serrated Dirk',
    3135: 'Void Staff',
    3137: 'Cryptbloom',
    3139: 'Mercurial Scimitar',
    3140: 'Quicksilver Sash',
    3142: 'Youmuu\'s Ghostblade',
    3143: 'Randuin\'s Omen',
    3145: 'Hextech Alternator',
    3146: 'Hextech Gunblade',
    3147: 'Haunting Guise',
    3152: 'Hextech Rocketbelt',
    3153: 'Blade of The Ruined King',
    3155: 'Hexdrinker',
    3156: 'Maw of Malmortius',
    3157: 'Zhonya\'s Hourglass',
    3158: 'Ionian Boots of Lucidity',
    3161: 'Spear of Shojin',
    3165: 'Morellonomicon',
    3172: 'Zephyr',
    3177: 'Guardian\'s Blade',
    3179: 'Umbral Glaive',
    3181: 'Hullbreaker',
    3184: 'Guardian\'s Hammer',
    3190: 'Locket of the Iron Solari',
    3193: 'Gargoyle Stoneplate',
    3211: 'Spectre\'s Cowl',
    3222: 'Mikael\'s Blessing',
    3302: 'Terminus',
    3330: 'Scarecrow Effigy',
    3340: 'Stealth Ward',
    3348: 'Arcane Sweeper',
    3349: 'Lucent Singularity',
    3363: 'Farsight Alteration',
    3364: 'Oracle Lens',
    3400: 'Your Cut',
    3430: 'Rite Of Ruin',
    3504: 'Ardent Censer',
    3508: 'Essence Reaver',
    3513: 'Eye of the Herald',
    3599: 'Kalista\'s Black Spear',
    3600: 'Kalista\'s Black Spear',
    3742: 'Dead Man\'s Plate',
    3748: 'Titanic Hydra',
    3801: 'Crystalline Bracer',
    3802: 'Lost Chapter',
    3803: 'Catalyst of Aeons',
    3814: 'Edge of Night',
    3850: 'Spellthief\'s Edge',
    3851: 'Frostfang',
    3853: 'Shard of True Ice',
    3854: 'Steel Shoulderguards',
    3855: 'Runesteel Spaulders',
    3857: 'Pauldrons of Whiterock',
    3858: 'Relic Shield',
    3859: 'Targon\'s Buckler',
    3860: 'Bulwark of the Mountain',
    3862: 'Spectral Sickle',
    3863: 'Harrowing Crescent',
    3864: 'Black Mist Scythe',
    3865: 'World Atlas',
    3866: 'Runic Compass',
    3867: 'Bounty of Worlds',
    3869: 'Celestial Opposition',
    3870: 'Dream Maker',
    3871: 'Zaz\'Zak\'s Realmspike',
    3876: 'Solstice Sleigh',
    3877: 'Bloodsong',
    3901: 'Fire at Will',
    3902: 'Death\'s Daughter',
    3903: 'Raise Morale',
    3916: 'Oblivion Orb',
    4003: 'Lifeline',
    4004: 'Spectral Cutlass',
    4005: 'Imperial Mandate',
    4010: 'Bloodletter\'s Curse',
    4011: 'Sword of Blossoming Dawn',
    4012: 'Sin Eater',
    4013: 'Lightning Braid',
    4014: 'Frozen Mallet',
    4015: 'Perplexity',
    4016: 'Wordless Promise',
    4017: 'Hellfire Hatchet',
    4401: 'Force of Nature',
    4402: 'Innervating Locket',
    4403: 'The Golden Spatula',
    4628: 'Horizon Focus',
    4629: 'Cosmic Drive',
    4630: 'Blighting Jewel',
    4632: 'Verdant Barrier',
    4633: 'Riftmaker',
    4635: 'Leeching Leer',
    4636: 'Night Harvester',
    4637: 'Demonic Embrace',
    4638: 'Watchful Wardstone',
    4641: 'Stirring Wardstone',
    4642: 'Bandleglass Mirror',
    4643: 'Vigilant Wardstone',
    4644: 'Crown of the Shattered Queen',
    4645: 'Shadowflame',
    4646: 'Stormsurge',
    6029: 'Ironspike Whip',
    6035: 'Silvermere Dawn',
    6333: 'Death\'s Dance',
    6609: 'Chempunk Chainsword',
    6610: 'Sundered Sky',
    6616: 'Staff of Flowing Water',
    6617: 'Moonstone Renewer',
    6620: 'Echoes of Helia',
    6621: 'Dawncore',
    6630: 'Goredrinker',
    6631: 'Stridebreaker',
    6632: 'Divine Sunderer',
    6653: 'Liandry\'s Torment',
    6655: 'Luden\'s Companion',
    6656: 'Everfrost',
    6657: 'Rod of Ages',
    6660: 'Bami\'s Cinder',
    6662: 'Iceborn Gauntlet',
    6664: 'Hollow Radiance',
    6665: 'Jak\'Sho, The Protean',
    6667: 'Radiant Virtue',
    6670: 'Noonquiver',
    6671: 'Galeforce',
    6672: 'Kraken Slayer',
    6673: 'Immortal Shieldbow',
    6675: 'Navori Quickblades',
    6676: 'The Collector',
    6677: 'Rageknife',
    6690: 'Rectrix',
    6691: 'Duskblade of Draktharr',
    6692: 'Eclipse',
    6693: 'Prowler\'s Claw',
    6694: 'Serylda\'s Grudge',
    6695: 'Serpent\'s Fang',
    6696: 'Axiom Arc',
    6697: 'Hubris',
    6698: 'Profane Hydra',
    6699: 'Voltaic Cyclosword',
    6700: 'Shield of the Rakkor',
    6701: 'Opportunity',
    7000: 'Sandshrike\'s Claw',
    7001: 'Syzygy',
    7002: 'Draktharr\'s Shadowcarver',
    7003: 'Rabadon\'s Deathcrown',
    7004: 'Enmity of the Masses',
    7005: 'Frozen Fist',
    7006: 'Typhoon',
    7007: 'Swordnado',
    7008: 'Ataraxia',
    7009: 'Icathia\'s Curse',
    7010: 'Vespertide',
    7011: 'Upgraded Aeropack',
    7012: 'Liandry\'s Lament',
    7013: 'Force of Arms',
    7014: 'Eternal Winter',
    7015: 'Ceaseless Hunger',
    7016: 'Dreamshatter',
    7017: 'Deicide',
    7018: 'Infinity Force',
    7019: 'Reliquary of the Golden Dawn',
    7020: 'Shurelya\'s Requiem',
    7021: 'Starcaster',
    7022: 'Certainty',
    7023: 'Equinox',
    7024: 'Caesura',
    7025: 'Leviathan',
    7026: 'The Unspoken Parasite',
    7027: 'Primordial Dawn',
    7028: 'Infinite Convergence',
    7029: 'Youmuu\'s Wake',
    7030: 'Seething Sorrow',
    7031: 'Edge of Finality',
    7032: 'Flicker',
    7033: 'Cry of the Shrieking City',
    7034: 'Hope Adrift',
    7035: 'Daybreak',
    7036: 'T.U.R.B.O.',
    7037: 'Obsidian Cleaver',
    7038: 'Shojin\'s Resolve',
    7039: 'Heavensfall',
    7040: 'Eye of the Storm',
    7041: 'Wyrmfallen Sacrifice',
    7042: 'The Baron\'s Gift',
    7050: 'Gangplank Placeholder',
    8001: 'Anathema\'s Chains',
    8020: 'Abyssal Mask',
}
SUMMONER_SPELLS = {
    21: "Barrier",
    1: "Cleanse",
    2202: "Flash",
    2201: "Flee",
    14: "Ignite",
    3: "Exhaust",
    4: "Flash",
    6: "Ghost",
    7: "Heal",
    13: "Clarity",
    30: "To the King!",
    31: "Poro Toss",
    11: "Smite",
    39: "Mark",
    32: "Mark",
    12: "Teleport",
    54: "Placeholder",
    55: "Placeholder and Attack-Smite"
}


def send_get_request(url):
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Nie udało się uzyskać informacji. URL: {url}, Status Code: {response.status_code}")
        return None


def get_account_info(summoner_name, summoner_tag, SERVER):
    url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{summoner_name}/{summoner_tag}"
    return send_get_request(url)


def get_account_info_by_puuid(puuid, SERVER):
    url = f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{puuid}"
    return send_get_request(url)


def get_summoner_info_puuid(puuid, SERVER):
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
    return send_get_request(url)


def get_team_info_puuid(summoner_id, SERVER):
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/clash/v1/players/by-summoner/{summoner_id}"
    return send_get_request(url)


def get_tournament_id_by_team(team_id, SERVER):
    url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/clash/v1/teams/{team_id}"
    return send_get_request(url)


def show_players_team(players, SERVER):
    players_info = []
    for selected in players:
        league_entries_url = f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/summoner/v4/summoners/{selected['summonerId']}"
        summoner_entries = send_get_request(league_entries_url)
        account_info = send_get_request(
            f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/riot/account/v1/accounts/by-puuid/{summoner_entries['puuid']}")
        game_name = account_info['gameName']
        tag_line = account_info['tagLine']

        profile_link = f"https://u.gg/lol/profile/{servers_to_region[SERVER][0]}/{game_name}-{tag_line}/overview"
        op_gg_link = f"https://www.op.gg/summoners/{servers_to_region[SERVER][2]}/{game_name}-{tag_line}"

        players_info.append([f"{game_name}#{tag_line}", profile_link, op_gg_link])

    return players_info


def calculate_time_ago(game_start_timestamp_ms):
    game_start_date = datetime.datetime.fromtimestamp(game_start_timestamp_ms / 1000)
    now = datetime.datetime.now()
    time_diff = now - game_start_date
    days_ago = time_diff.days
    seconds_ago = time_diff.seconds
    hours_ago = seconds_ago // 3600
    minutes_ago = (seconds_ago % 3600) // 60

    if days_ago >= 7:
        weeks_ago = days_ago // 7
        return f"{weeks_ago} weeks ago"
    elif days_ago >= 1:
        return f"{days_ago} days ago"
    elif hours_ago >= 1:
        return f"{hours_ago} hours ago"
    elif minutes_ago >= 1:
        return f"{minutes_ago} minutes ago"
    else:
        return "Just now"


def get_match_participant_details(match_details, puuid, SERVER):
    participant_details_list = []
    flag = 1
    for participant in match_details["info"]["participants"]:

        game_start_timestamp_ms = match_details["info"].get("gameStartTimestamp", 0)
        participant_details = {
            "Champion": participant.get("championName", ""),
            "Summoner Name": participant.get("summonerName", ""),
            "summoner_tag": participant.get("riotIdTagline"),
            "KDA": f'{participant.get("kills", 0)}/{participant.get("deaths", 0)}/{participant.get("assists", 0)}',
            "Items": [(participant.get(f'item{i}'), ITEMS.get(participant.get(f'item{i}'), "")) for i in range(7) if participant.get(f'item{i}', 0) in ITEMS],
            "Primary Rune Path": (participant["perks"]["styles"][0].get("style"), RUNES_AND_SHARDS.get(participant["perks"]["styles"][0].get("style"), "")),
            "Primary Rune": (participant["perks"]["styles"][0]["selections"][0].get("perk"), RUNES_AND_SHARDS.get(participant["perks"]["styles"][0]["selections"][0].get("perk"), "")),
            "Secondary Rune Path": (participant["perks"]["styles"][1].get("style"), RUNES_AND_SHARDS.get(participant["perks"]["styles"][1].get("style"), "")),
            "Primary Runes": [(selection.get("perk"), RUNES_AND_SHARDS.get(selection.get("perk"), "")) for selection in participant["perks"]["styles"][0].get("selections", [])],
            "Secondary Runes": [(selection.get("perk"), RUNES_AND_SHARDS.get(selection.get("perk"), "")) for selection in participant["perks"]["styles"][1].get("selections", [])],
            "Shards": [(shard, RUNES_AND_SHARDS.get(shard, "")) for shard in  participant["perks"]["statPerks"].values()],
            "CS": participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
            "Team ID": participant.get("teamId", "Unknown")
        }
        participant_details["Control Wards"] = participant.get('visionWardsBoughtInGame', 0)
        participant_details["Summoner Spells"] = [
            (participant.get('summoner1Id'), SUMMONER_SPELLS.get(participant.get('summoner1Id'), "")),
            (participant.get('summoner2Id'), SUMMONER_SPELLS.get(participant.get('summoner2Id'), ""))
        ]
        game_duration = divmod(match_details['info'].get('gameDuration', 0), 60)
        participant_details["Game Duration"] = f"{game_duration[0]}:{game_duration[1]:02d}"
        # Dodatkowe pola dla uczestnika, który jest głównym graczem
        if participant.get("puuid") == puuid:
            if flag:
                participant_details["summonerId"] = participant.get("summonerId")
            participant_details["gameStartTimestamp"] = match_details["info"].get("gameStartTimestamp", 0)
            participant_details["Match Result"] = 'Win' if participant.get('win', False) else 'Lose'
            participant_details["Start Date"] = datetime.datetime.fromtimestamp(game_start_timestamp_ms / 1000).strftime('%d/%m/%Y %H:%M')
            participant_details["Start Game Ago"] = calculate_time_ago(game_start_timestamp_ms)
            game_duration = divmod(match_details['info'].get('gameDuration', 0), 60)
            participant_details["Game Duration"] = f"{game_duration[0]}:{game_duration[1]:02d}"
            participant_details["Kill Participation"] = f"{participant['challenges'].get('killParticipation', 0) * 100:.0f}%"
            participant_details_list.insert(0, participant_details)
        else:
            participant_details_list.append(participant_details)

    return participant_details_list


def sort_participants(participants, main_player_team_id):

    team_members = [p for p in participants[1:] if p['Team ID'] == main_player_team_id]
    opposite_team_members = [p for p in participants[1:] if p['Team ID'] != main_player_team_id]
    sorted_participants = [participants[0]] + team_members + opposite_team_members
    return sorted_participants


def display_matches(summoner_name, summoner_tag, SERVER):
    account_info = get_account_info(summoner_name,summoner_tag,SERVER)

    puuid = account_info["puuid"]

    match_ids_list = send_get_request(
        f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start=0&count=20")
    match_history_list = []
    for match_id in match_ids_list:

        match_details = send_get_request(
            f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/{match_id}")
        participant_details = get_match_participant_details(match_details, puuid, SERVER)
        match_history_list.append(participant_details)
    match_history_list_sorted=[]
    for match in match_history_list:
        match_history_list_sorted.append(sort_participants(match, match[0]['Team ID']))
        print(match)

    # tmp = send_get_request(
    #     f"https://{servers_to_region[SERVER][0]}.api.riotgames.com/lol/league/v4/entries/by-summoner/{match_history_list_sorted[0][0]["summonerId"]}")
    #
    # print(f"{tmp[0]['queueType'][7:11]} = {tmp[0]['tier']}{tmp[0]['rank']} {tmp[0]['leaguePoints']}lp")
    match_history_list_sorted[0][0]["SERVER"] = SERVER
    match_history_list_sorted[0][0]["summoner_name"] = summoner_name
    match_history_list_sorted[0][0]["summoner_tag"] = summoner_tag
    return match_history_list_sorted


def display_matches_by_value(summoner_name, summoner_tag, SERVER, current_count, limit):
    account_info = get_account_info(summoner_name,summoner_tag,SERVER)
    puuid = account_info["puuid"]
    match_ids_list = send_get_request(
        f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/by-puuid/{puuid}/ids?type=ranked&start={current_count}&count={limit}")
    match_history_list = []

    for match_id in match_ids_list:
        match_details = send_get_request(
            f"https://{servers_to_region[SERVER][1]}.api.riotgames.com/lol/match/v5/matches/{match_id}")
        participant_details = get_match_participant_details(match_details, puuid,SERVER)
        match_history_list.append(participant_details)
    match_history_list_sorted=[]
    for match in match_history_list:
        match_history_list_sorted.append(sort_participants(match, match[0]['Team ID']))
    return match_history_list_sorted