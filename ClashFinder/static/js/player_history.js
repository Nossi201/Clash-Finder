//player_hitory.js
let current_count = 20;
let current_count_tmp = 20;
let match_list = [];

function addMatchToArray(tmp) {
    match_list.push(tmp);
}
function addMatchToDOM(match, server) {

    const matchCard = document.createElement('div');
    const matchResultClass = match[0]['Match Result'] === 'Win' ? 'card-win' : match[0]['Match Result'] === 'Lose' ? 'card-loss' : 'card-draw';
    matchCard.className = `card mb-3 ${matchResultClass}`;

    const detailsHTML = `
    <div class="row row-margin5px margin-0" hidden>
        <div class="col-md-6">
            <div class="upper-part d-flex flex-row">
                <div class="col-md-2">A</div>
                <div class="col-md-2">KDA</div>
                <div class="col-md-1">CS</div>
                <div class="col-md-1">C.W</div>
                <div class="col-md-6">Items</div>
            </div>
            ${match.slice(0, 5).map(player => `
            <div class="upper-part d-flex flex-row">
                <div class="col-md-1">
                    <img src="/static/img/champion/${player.Champion}.png" alt="${player.Champion}" class="array-icon-1">
                </div>
                <div class="col-md-1">
                    <div class="d-flex">
                        <img src="/static/img/spells/summoner/${player['Summoner Spells'][0][0]}.png" alt="Spell1" class="array-icon-2">
                        <img src="/static/img/runes_and_shards/${player['Primary Rune'][0]}.png" alt="Primary Rune" class="array-icon-2">
                    </div>
                    <div class="d-flex">
                        <img src="/static/img/spells/summoner/${player['Summoner Spells'][1][0]}.png" alt="Spell1" class="array-icon-2">
                        <img src="/static/img/runes_and_shards/${player['Primary Rune'][0]}.png" alt="Primary Rune" class="array-icon-2">
                    </div>
                </div>
                <div class="col-md-2">${player.KDA}</div>
                <div class="col-md-1">${player.CS}</div>
                <div class="col-md-1">${player["Control Wards"]}</div>
                <div class="col-md-6">
                    ${player["Items"].map(item => `<img src="/static/img/item/${item[0]}.png" alt="Item" class="array-icon-1">`).join('')}
                </div>
            </div>
            `).join('')}
        </div>
        <div class="col-md-6">
            <div class="upper-part d-flex flex-row">
                <div class="col-md-2">A</div>
                <div class="col-md-2">KDA</div>
                <div class="col-md-1">CS</div>
                <div class="col-md-1">C.W</div>
                <div class="col-md-6">Items</div>
            </div>
            ${match.slice(5, 10).map(player => `
            <div class="upper-part d-flex flex-row">
                <div class="col-md-1">
                    <img src="/static/img/champion/${player.Champion}.png" alt="${player.Champion}" class="array-icon-1">
                </div>
                <div class="col-md-1">
                    <div class="d-flex">
                        <img src="/static/img/spells/summoner/${player['Summoner Spells'][0][0]}.png" alt="Spell1" class="array-icon-2">
                        <img src="/static/img/runes_and_shards/${player['Primary Rune'][0]}.png" alt="Primary Rune" class="array-icon-2">
                    </div>
                    <div class="d-flex">
                        <img src="/static/img/spells/summoner/${player['Summoner Spells'][1][0]}.png" alt="Spell1" class="array-icon-2">
                        <img src="/static/img/runes_and_shards/${player['Primary Rune'][0]}.png" alt="Primary Rune" class="array-icon-2">
                    </div>
                </div>
                <div class="col-md-2">${player.KDA}</div>
                <div class="col-md-1">${player.CS}</div>
                <div class="col-md-1">${player["Control Wards"]}</div>
                <div class="col-md-6">
                    ${player["Items"].map(item => `<img src="/static/img/item/${item[0]}.png" alt="Item" class="array-icon-1">`).join('')}
                </div>
            </div>
            `).join('')}
        </div>
    </div>`;


    // Zakładając, że dane meczu są w pierwszym elemencie tablicy, czyli match[0]
    const matchDetails = match[0];
    const itemsHTML = matchDetails["Items"].map(item => item[0] ? `<img src="/static/img/item/${item[0]}.png" alt="Item" class="item-icon">` : '').join('');
    let teamOneHTML = '';
    let teamTwoHTML = '';
    console.log(match)
    match.forEach((player, index)=>{
     const playerHTML = `
            <img src="/static/img/champion/${player['Champion']}.png" alt="${player['Champion']}" class="team-icon">
            <a href="/player_stats/${player['Summoner Name']}%23${player['summoner_tag']}/${server}" class="player-name">
                                        ${player["Summoner Name"]}#${player["summoner_tag"]}
                                    </a><br>
        `;

        if (index < 5) { // Zakładamy, że pierwszych 5 graczy to drużyna 1
            teamOneHTML += playerHTML;
        } else { // Reszta graczy to drużyna 2
            teamTwoHTML += playerHTML;
        }
    });
    matchCard.innerHTML = `
        <div class="row row-margin5px">
            <div class="col-md-2">
                <p title='${matchDetails["Start Date"]}'>Date: ${matchDetails["Start Game Ago"]}</p>
                <p>Duration: ${matchDetails["Game Duration"]}</p>
                <p>Result: ${matchDetails["Match Result"]}</p>
                <p class="kda-text">KDA: ${matchDetails["KDA"]}</p>
            </div>
            <div class="col-md-3">
                <div class="upper-part d-flex flex-row">
                    <div class="g1-spells-runes d-flex flex-column justify-content-around">
                        <img src="/static/img/champion/${matchDetails['Champion']}.png" alt="${matchDetails['Champion']}" class="icons_main">
                    </div>
                        <div class="g1-spells-runes d-flex flex-column justify-content-around">
                            <div class="d-flex">
                                <img src="/static/img/spells/summoner/${matchDetails['Summoner Spells'][0][0]}.png" alt="Spell1" class="spell-icon">
                                <img src="/static/img/runes_and_shards/${matchDetails['Primary Rune'][0]}.png" alt="Spell2" class="spell-icon">
                            </div>
                            <div class="d-flex">
                                <img src="/static/img/spells/summoner/${matchDetails['Summoner Spells'][1][0]}.png" alt="Spell2" class="spell-icon">
                                <img src="/static/img/runes_and_shards/${matchDetails['Secondary Rune Path'][0]}.png" alt="Spell1" class="spell-icon">

                            </div>
                        </div>
                </div>
                <div class="lower-part items-container">${itemsHTML}</div>
            </div>
            <div class="col-md-1">
                        <p class="cs-text" title="Creep Score">CS : ${matchDetails["CS"] }</p>
                        <p class="stats-text" title="Control Wards">C.W : ${matchDetails["Control Wards"] }</p>
                        <p class="stats-text" title="Kill Participation">K.P : ${matchDetails["Kill Participation"] }</p>
                    </div>
            <div class="col-md-4">
                        <div class="row">
                    <div class="col-6 team">
                        ${teamOneHTML}
                    </div>
                    <div class="col-6 team">
                        ${teamTwoHTML}
                    </div>
                </div>
            </div>
            <div class="col button-column">
                        <button class="btn btn-primary btn-color toggle-details"id="All-Player-Button-Match-${current_count_tmp}">Show Stats</button>
                    </div>

        </div>
        ${detailsHTML}
    `;
    current_count_tmp +=1;
    const container = document.getElementById('addUpp');
    container.parentNode.insertBefore(matchCard, container);
}
document.addEventListener('click', function(event) {
    if (event.target.classList.contains('toggle-details')) {
        const card = event.target.closest('.card');
        const details = card.querySelector('.row-margin5px.margin-0');
        details.hidden = !details.hidden;
    }
});
document.getElementById('loadMoreMatchesButton').addEventListener('click', function() {
    const number = parseInt(document.getElementById('number-list').value, 10); // Konwersja na liczbę
    const server = document.getElementById('server').value;
    const summonerName = document.getElementById('summonerName').value;
    const summonerTag = document.getElementById('summonerTag').value;
    fetch('/load_more_matches', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            current_count: current_count,
            number: number,
            server: server,
            SUMMONER_NAME: summonerName,
            SUMMONER_TAG: summonerTag
        })
    })
    .then(response => response.json())
    .then(data => {
        current_count += number;

        data.forEach(match => addMatchToDOM(match, server));


    })
    .catch(error => console.error('Error:', error));
});