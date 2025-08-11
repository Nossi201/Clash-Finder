// static/js/match-renderer.js
// Match rendering module with CDN support - POPRAWKA: Dodano runy

console.log('🎨 Match Renderer module loaded');

const MatchRenderer = {

    async renderMatchCard(match, matchIndex) {
        console.log(`🎨 Rendering match ${matchIndex}...`);

        const mainPlayer = match[0];
        if (!mainPlayer) {
            console.error('❌ No main player data for match', matchIndex);
            return '';
        }

        const resultClass = this.getResultClass(mainPlayer['Match Result']);

        // Generate all images with CDN - POPRAWKA: Dodano runy
        const images = await this.generateAllImages(mainPlayer);

        // Generate items HTML
        const itemsHtml = await this.generateItemsHtml(mainPlayer['Items']);

        // Generate team compositions
        const team1Html = await this.generateTeamHtml(match.slice(0, 5));
        const team2Html = await this.generateTeamHtml(match.slice(5));

        // Generate detailed stats
        const detailedStatsHtml = await this.generateDetailedStats(match);

        const matchHtml = `
            <div class="card mb-3 ${resultClass}">
                <div class="row row-margin5px">
                    <div class="col-md-2">
                        <p title='${mainPlayer["Start Date"] || ''}'>Date: ${mainPlayer["Start Game Ago"] || 'Unknown'}</p>
                        <p>Duration: ${mainPlayer["Game Duration"] || 'Unknown'}</p>
                        <p>Result: ${mainPlayer["Match Result"] || 'Unknown'}</p>
                        <p class="kda-text">KDA: ${mainPlayer["KDA"] || 'Unknown'}</p>
                    </div>

                    <div class="col-md-3">
                        <div class="upper-part d-flex flex-row">
                            <div class="g1-spells-runes d-flex flex-column justify-content-around">
                                ${images.champion}
                            </div>
                            <!-- POPRAWKA: Dodano runy obok summoner spells -->
                            <div class="g1-spells-runes d-flex flex-column justify-content-around">
                                <div class="d-flex">
                                    ${images.spell1}
                                    ${images.primaryRune}
                                </div>
                                <div class="d-flex">
                                    ${images.spell2}
                                    ${images.secondaryRune}
                                </div>
                            </div>
                        </div>
                        <div class="lower-part items-container">
                            ${itemsHtml}
                        </div>
                    </div>

                    <div class="col-md-1">
                        <p class="cs-text" title="Creep Score">CS: ${mainPlayer["CS"] || 0}</p>
                        <p class="stats-text" title="Control Wards">C.W: ${mainPlayer["Control Wards"] || 0}</p>
                        <p class="stats-text" title="Kill Participation">K.P: ${mainPlayer["Kill Participation"] || 'N/A'}</p>
                    </div>

                    <div class="col-md-4">
                        <div class="row">
                            <div class="col-6 team">${team1Html}</div>
                            <div class="col-6 team">${team2Html}</div>
                        </div>
                    </div>

                    <div class="col button-column">
                        <button class="btn-primary btn-color toggle-details"
                                id="All-Player-Button-Match-${matchIndex}">
                            Show Stats
                        </button>
                    </div>
                </div>

                <div class="row row-margin5px margin-0" hidden>
                    ${detailedStatsHtml}
                </div>
            </div>
        `;

        console.log(`✅ Match ${matchIndex} rendered successfully`);
        return matchHtml;
    },

    getResultClass(result) {
        switch(result) {
            case 'Win': return 'card-win';
            case 'Lose': return 'card-loss';
            default: return 'card-draw';
        }
    },

    async generateAllImages(mainPlayer) {
        console.log('🖼️ Generating main player images...');

        // POPRAWKA: Dodano generowanie obrazków run
        return {
            champion: await CDNUtils.createImageElement(
                CDNUtils.getChampionImageUrl(mainPlayer['Champion']),
                mainPlayer['Champion'],
                'icons_main'
            ),
            spell1: await CDNUtils.createImageElement(
                CDNUtils.getSummonerSpellImageUrl(mainPlayer['Summoner Spells'][0][0]),
                'Spell1',
                'spell-icon'
            ),
            spell2: await CDNUtils.createImageElement(
                CDNUtils.getSummonerSpellImageUrl(mainPlayer['Summoner Spells'][1][0]),
                'Spell2',
                'spell-icon'
            ),
            // POPRAWKA: Dodano Primary Rune
            primaryRune: await CDNUtils.createImageElement(
                CDNUtils.getRuneImageUrl(mainPlayer['Primary Rune'][0]),
                'Primary Rune',
                'rune-icon'
            ),
            // POPRAWKA: Dodano Secondary Rune Style
            secondaryRune: await CDNUtils.createImageElement(
                CDNUtils.getRuneStyleImageUrl(mainPlayer['Secondary Rune Path'][0]),
                'Secondary Rune',
                'rune-icon'
            )
        };
    },

    async generateItemsHtml(items) {
        console.log('🛡️ Generating items HTML...');

        let itemsHtml = '';

        // Add actual items
        for (const item of items) {
            if (item[0] !== 0) {
                itemsHtml += await CDNUtils.createImageElement(
                    CDNUtils.getItemImageUrl(item[0]),
                    'Item',
                    'item-icon',
                    'empty-slot'
                );
            } else {
                itemsHtml += '<div class="item-icon empty-slot"></div>';
            }
        }

        // Fill remaining slots to 7
        const itemsCount = items.length;
        for (let i = itemsCount; i < 7; i++) {
            itemsHtml += '<div class="item-icon empty-slot"></div>';
        }

        return itemsHtml;
    },

    async generateTeamHtml(teamPlayers) {
        console.log('👥 Generating team HTML...');

        let html = '';

        for (const player of teamPlayers) {
            const championImg = await CDNUtils.createImageElement(
                CDNUtils.getChampionImageUrl(player['Champion']),
                player['Champion'],
                'team-icon'
            );

            const playerName = player['summoner_tag']
                ? `${player['Summoner Name']}#${player['summoner_tag']}`
                : player['Summoner Name'];

            const currentServer = document.getElementById('server')?.value?.toLowerCase()?.replace(' ', '-')?.replace('&', 'and') || 'eu-west';
            const playerUrl = `/player_stats/${playerName.replace('#', '--').replace(' ', '-')}/${currentServer}`;

            html += `
                ${championImg}
                <a href="${playerUrl}" class="player-name">${playerName}</a><br>
            `;
        }

        return html;
    },

    async generateDetailedStats(match) {
        console.log('📊 Generating detailed stats...');

        const team1Html = await this.generateDetailedTeamStats(match.slice(0, 5));
        const team2Html = await this.generateDetailedTeamStats(match.slice(5));

        return `
            <div class="col-md-6">
                <div class="upper-part d-flex flex-row">
                    <div class="col-md-2">C</div>
                    <div class="col-md-2">KDA</div>
                    <div class="col-md-1">CS</div>
                    <div class="col-md-1">C.W</div>
                    <div class="col-md-6">Items</div>
                </div>
                ${team1Html}
            </div>
            <div class="col-md-6">
                <div class="upper-part d-flex flex-row">
                    <div class="col-md-2">C</div>
                    <div class="col-md-2">KDA</div>
                    <div class="col-md-1">CS</div>
                    <div class="col-md-1">C.W</div>
                    <div class="col-md-6">Items</div>
                </div>
                ${team2Html}
            </div>
        `;
    },

    async generateDetailedTeamStats(teamPlayers) {
        console.log('📋 Generating detailed team stats...');

        let html = '';

        for (const player of teamPlayers) {
            const championImg = await CDNUtils.createImageElement(
                CDNUtils.getChampionImageUrl(player['Champion']),
                player['Champion'],
                'array-icon-1'
            );

            const spell1Img = await CDNUtils.createImageElement(
                CDNUtils.getSummonerSpellImageUrl(player['Summoner Spells'][0][0]),
                'Spell1',
                'array-icon-2'
            );

            const spell2Img = await CDNUtils.createImageElement(
                CDNUtils.getSummonerSpellImageUrl(player['Summoner Spells'][1][0]),
                'Spell2',
                'array-icon-2'
            );

            // POPRAWKA: Dodano runy w szczegółowych statystykach
            const primaryRuneImg = await CDNUtils.createImageElement(
                CDNUtils.getRuneImageUrl(player['Primary Rune'][0]),
                'Primary Rune',
                'array-icon-2'
            );

            const secondaryRuneImg = await CDNUtils.createImageElement(
                CDNUtils.getRuneStyleImageUrl(player['Secondary Rune Path'][0]),
                'Secondary Rune',
                'array-icon-2'
            );

            // Generate items for detailed view
            let itemsHtml = '';
            for (const item of player['Items']) {
                if (item[0] !== 0) {
                    itemsHtml += await CDNUtils.createImageElement(
                        CDNUtils.getItemImageUrl(item[0]),
                        'Item',
                        'array-icon-1',
                        'empty-slot'
                    );
                } else {
                    itemsHtml += '<div class="array-icon-1 empty-slot"></div>';
                }
            }

            // Add empty slots
            const itemsCount = player['Items'].length;
            for (let i = itemsCount; i < 7; i++) {
                itemsHtml += '<div class="array-icon-1 empty-slot"></div>';
            }

            html += `
                <div class="upper-part d-flex flex-row">
                    <div class="col-md-1">${championImg}</div>
                    <div class="col-md-1">
                        <div class="d-flex">${spell1Img}${primaryRuneImg}</div>
                        <div class="d-flex">${spell2Img}${secondaryRuneImg}</div>
                    </div>
                    <div class="col-md-2">${player['KDA'] || 'N/A'}</div>
                    <div class="col-md-1">${player['CS'] || 0}</div>
                    <div class="col-md-1">${player['Control Wards'] || 0}</div>
                    <div class="col-md-6">${itemsHtml}</div>
                </div>
            `;
        }

        return html;
    },

    // Add rendered match to DOM
    addMatchToDOM(matchHtml) {
        const container = document.querySelector('.main-content');
        const form = document.getElementById('addUpp');

        if (!container || !form) {
            console.error('❌ Container or form not found');
            return false;
        }

        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = matchHtml;

        if (tempDiv.firstElementChild) {
            container.insertBefore(tempDiv.firstElementChild, form);
            console.log('✅ Match added to DOM');

            // IMPORTANT: Re-initialize toggle for new elements
            // No need to call ToggleHandler.init() again since we use event delegation

            return true;
        }

        return false;
    }
};

// Make MatchRenderer available globally
window.MatchRenderer = MatchRenderer;