# app/models/game_models.py
"""
Game data models for Clash Finder.
Represents League of Legends game entities and structures.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class Account:
    """Riot Account information."""
    puuid: str
    game_name: str
    tag_line: str

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Account':
        """Create Account from Riot API response."""
        return cls(
            puuid=data['puuid'],
            game_name=data['gameName'],
            tag_line=data['tagLine']
        )


@dataclass
class Summoner:
    """League of Legends summoner information."""
    id: str
    account_id: str
    puuid: str
    profile_icon_id: int
    summoner_level: int
    revision_date: int

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Summoner':
        """Create Summoner from Riot API response."""
        return cls(
            id=data['id'],
            account_id=data['accountId'],
            puuid=data['puuid'],
            profile_icon_id=data['profileIconId'],
            summoner_level=data['summonerLevel'],
            revision_date=data['revisionDate']
        )


@dataclass
class Item:
    """Item in a match."""
    item_id: int
    slot: int

    def __bool__(self) -> bool:
        """Item exists if ID is not 0."""
        return self.item_id != 0


@dataclass
class Rune:
    """Rune selection."""
    primary_style: int
    sub_style: int
    perks: List[int] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Rune':
        """Create Rune from API perks data."""
        styles = data.get('styles', [])

        primary_style = 0
        sub_style = 0
        perks = []

        if len(styles) > 0:
            primary_style = styles[0].get('style', 0)
            primary_selections = styles[0].get('selections', [])
            perks.extend([s['perk'] for s in primary_selections])

        if len(styles) > 1:
            sub_style = styles[1].get('style', 0)
            sub_selections = styles[1].get('selections', [])
            perks.extend([s['perk'] for s in sub_selections])

        return cls(
            primary_style=primary_style,
            sub_style=sub_style,
            perks=perks
        )


@dataclass
class ParticipantStats:
    """Detailed statistics for a match participant."""
    kills: int
    deaths: int
    assists: int
    champion_name: str
    champion_id: int
    summoner_name: str
    summoner_tag: str
    puuid: str
    team_id: int
    win: bool

    # Combat stats
    total_damage_dealt: int = 0
    total_damage_dealt_to_champions: int = 0
    total_damage_taken: int = 0
    total_heal: int = 0
    gold_earned: int = 0

    # CS and vision
    total_minions_killed: int = 0
    neutral_minions_killed: int = 0
    vision_score: int = 0
    wards_placed: int = 0
    wards_killed: int = 0

    # Items and builds
    items: List[Item] = field(default_factory=list)
    runes: Optional[Rune] = None
    summoner_spells: List[int] = field(default_factory=list)

    # Game specifics
    champion_level: int = 0
    team_position: str = ""
    individual_position: str = ""

    # Multikills and special
    double_kills: int = 0
    triple_kills: int = 0
    quadra_kills: int = 0
    penta_kills: int = 0
    killing_sprees: int = 0
    largest_killing_spree: int = 0

    @property
    def kda(self) -> float:
        """Calculate KDA ratio."""
        if self.deaths == 0:
            return float(self.kills + self.assists)
        return (self.kills + self.assists) / self.deaths

    @property
    def cs(self) -> int:
        """Total creep score."""
        return self.total_minions_killed + self.neutral_minions_killed

    @property
    def cs_per_min(self) -> float:
        """Creep score per minute."""
        return 0.0  # Calculated with game duration

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'ParticipantStats':
        """Create ParticipantStats from API participant data."""
        # Extract items
        items = []
        for i in range(7):  # Items 0-6
            item_id = data.get(f'item{i}', 0)
            if item_id:
                items.append(Item(item_id=item_id, slot=i))

        # Extract runes
        runes = None
        if 'perks' in data:
            runes = Rune.from_api(data['perks'])

        # Extract summoner spells
        summoner_spells = [
            data.get('summoner1Id', 0),
            data.get('summoner2Id', 0)
        ]

        return cls(
            kills=data.get('kills', 0),
            deaths=data.get('deaths', 0),
            assists=data.get('assists', 0),
            champion_name=data.get('championName', ''),
            champion_id=data.get('championId', 0),
            summoner_name=data.get('riotIdGameName', data.get('summonerName', '')),
            summoner_tag=data.get('riotIdTagline', ''),
            puuid=data.get('puuid', ''),
            team_id=data.get('teamId', 0),
            win=data.get('win', False),

            total_damage_dealt=data.get('totalDamageDealt', 0),
            total_damage_dealt_to_champions=data.get('totalDamageDealtToChampions', 0),
            total_damage_taken=data.get('totalDamageTaken', 0),
            total_heal=data.get('totalHeal', 0),
            gold_earned=data.get('goldEarned', 0),

            total_minions_killed=data.get('totalMinionsKilled', 0),
            neutral_minions_killed=data.get('neutralMinionsKilled', 0),
            vision_score=data.get('visionScore', 0),
            wards_placed=data.get('wardsPlaced', 0),
            wards_killed=data.get('wardsKilled', 0),

            items=items,
            runes=runes,
            summoner_spells=summoner_spells,

            champion_level=data.get('champLevel', 0),
            team_position=data.get('teamPosition', ''),
            individual_position=data.get('individualPosition', ''),

            double_kills=data.get('doubleKills', 0),
            triple_kills=data.get('tripleKills', 0),
            quadra_kills=data.get('quadraKills', 0),
            penta_kills=data.get('pentaKills', 0),
            killing_sprees=data.get('killingSprees', 0),
            largest_killing_spree=data.get('largestKillingSpree', 0)
        )


@dataclass
class TeamStats:
    """Team statistics for a match."""
    team_id: int
    win: bool

    # Objectives
    baron_kills: int = 0
    dragon_kills: int = 0
    rift_herald_kills: int = 0
    tower_kills: int = 0
    inhibitor_kills: int = 0

    # Bans
    bans: List[int] = field(default_factory=list)

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'TeamStats':
        """Create TeamStats from API team data."""
        objectives = data.get('objectives', {})

        bans = [ban.get('championId', -1) for ban in data.get('bans', [])]

        return cls(
            team_id=data.get('teamId', 0),
            win=data.get('win', False),
            baron_kills=objectives.get('baron', {}).get('kills', 0),
            dragon_kills=objectives.get('dragon', {}).get('kills', 0),
            rift_herald_kills=objectives.get('riftHerald', {}).get('kills', 0),
            tower_kills=objectives.get('tower', {}).get('kills', 0),
            inhibitor_kills=objectives.get('inhibitor', {}).get('kills', 0),
            bans=bans
        )


@dataclass
class Match:
    """Complete match information."""
    match_id: str
    game_creation: int
    game_duration: int
    game_mode: str
    game_type: str
    queue_id: int

    participants: List[ParticipantStats] = field(default_factory=list)
    teams: List[TeamStats] = field(default_factory=list)

    @property
    def game_creation_datetime(self) -> datetime:
        """Game creation as datetime object."""
        return datetime.fromtimestamp(self.game_creation / 1000)

    @property
    def duration_minutes(self) -> float:
        """Game duration in minutes."""
        return self.game_duration / 60

    def get_participant_by_puuid(self, puuid: str) -> Optional[ParticipantStats]:
        """Find participant by PUUID."""
        for participant in self.participants:
            if participant.puuid == puuid:
                return participant
        return None

    def get_team(self, team_id: int) -> Optional[TeamStats]:
        """Get team by ID."""
        for team in self.teams:
            if team.team_id == team_id:
                return team
        return None

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'Match':
        """Create Match from API match data."""
        info = data.get('info', {})
        metadata = data.get('metadata', {})

        # Parse participants
        participants = [
            ParticipantStats.from_api(p)
            for p in info.get('participants', [])
        ]

        # Parse teams
        teams = [
            TeamStats.from_api(t)
            for t in info.get('teams', [])
        ]

        return cls(
            match_id=metadata.get('matchId', ''),
            game_creation=info.get('gameCreation', 0),
            game_duration=info.get('gameDuration', 0),
            game_mode=info.get('gameMode', ''),
            game_type=info.get('gameType', ''),
            queue_id=info.get('queueId', 0),
            participants=participants,
            teams=teams
        )


@dataclass
class ClashPlayer:
    """Clash tournament player information."""
    summoner_id: str
    summoner_name: str
    summoner_tag: str
    position: str
    role: str

    # Additional stats if available
    tier: Optional[str] = None
    rank: Optional[str] = None
    wins: int = 0
    losses: int = 0

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'ClashPlayer':
        """Create ClashPlayer from API data."""
        return cls(
            summoner_id=data.get('summonerId', ''),
            summoner_name=data.get('summonerName', ''),
            summoner_tag=data.get('summonerTag', ''),
            position=data.get('position', ''),
            role=data.get('role', '')
        )


@dataclass
class ClashTeam:
    """Clash tournament team information."""
    team_id: str
    tournament_id: int
    name: str
    abbreviation: str
    tier: int

    players: List[ClashPlayer] = field(default_factory=list)

    captain_id: Optional[str] = None
    icon_id: int = 0

    @classmethod
    def from_api(cls, data: Dict[str, Any]) -> 'ClashTeam':
        """Create ClashTeam from API data."""
        players = [
            ClashPlayer.from_api(p)
            for p in data.get('players', [])
        ]

        return cls(
            team_id=data.get('id', ''),
            tournament_id=data.get('tournamentId', 0),
            name=data.get('name', ''),
            abbreviation=data.get('abbreviation', ''),
            tier=data.get('tier', 0),
            players=players,
            captain_id=data.get('captain', None),
            icon_id=data.get('iconId', 0)
        )


@dataclass
class MatchHistory:
    """Collection of matches for a player."""
    puuid: str
    matches: List[Match] = field(default_factory=list)

    @property
    def total_matches(self) -> int:
        """Total number of matches."""
        return len(self.matches)

    @property
    def wins(self) -> int:
        """Count wins."""
        count = 0
        for match in self.matches:
            participant = match.get_participant_by_puuid(self.puuid)
            if participant and participant.win:
                count += 1
        return count

    @property
    def losses(self) -> int:
        """Count losses."""
        return self.total_matches - self.wins

    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage."""
        if self.total_matches == 0:
            return 0.0
        return (self.wins / self.total_matches) * 100

    def add_match(self, match: Match) -> None:
        """Add a match to history."""
        self.matches.append(match)

    def get_recent_matches(self, count: int = 10) -> List[Match]:
        """Get most recent matches."""
        return self.matches[:count]