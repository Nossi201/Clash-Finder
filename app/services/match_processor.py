# app/services/match_processor.py
"""
Match processor for transforming raw match data into display format.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from app.services.game_constants import QUEUES, CHAMPIONS, ITEMS, SUMMONER_SPELLS
from config.logging_config import get_logger

logger = get_logger('services.match_processor')


class MatchProcessor:
    """Process raw match data into display format."""

    def process_match(
        self,
        match_data: Dict[str, Any],
        puuid: str,
        game_name: str,
        tag_line: str,
        server: str
    ) -> Optional[Dict[str, Any]]:
        """
        Process raw match data for display.

        Args:
            match_data: Raw match data from API
            puuid: Player's PUUID
            game_name: Player's game name
            tag_line: Player's tag line
            server: Server

        Returns:
            Processed match data or None
        """
        try:
            info = match_data.get('info', {})
            metadata = match_data.get('metadata', {})

            # Find player's participant data
            participant = self._find_participant(info.get('participants', []), puuid)
            if not participant:
                logger.warning(f"Player not found in match {metadata.get('matchId')}")
                return None

            # Get all participants for both teams
            all_participants = self._process_all_participants(info.get('participants', []))

            # Process basic match info
            processed = {
                # Match identification
                'match_id': metadata.get('matchId'),
                'game_id': info.get('gameId'),

                # Player identification
                'puuid': puuid,
                'summoner_name': game_name,
                'summoner_tag': tag_line,
                'server': server,

                # Match info
                'game_mode': self._get_game_mode(info.get('gameMode')),
                'queue_type': self._get_queue_type(info.get('queueId')),
                'queue_id': info.get('queueId'),
                'game_duration': self._format_duration(info.get('gameDuration')),
                'game_duration_seconds': info.get('gameDuration'),
                'game_creation': info.get('gameCreation'),
                'game_end': info.get('gameEndTimestamp'),
                'time_ago': self._calculate_time_ago(info.get('gameEndTimestamp')),

                # Win/Loss
                'is_win': participant.get('win', False),
                'is_remake': info.get('gameDuration', 0) < 240,  # Less than 4 minutes

                # Champion info
                'champion_id': participant.get('championId'),
                'champion_name': self._get_champion_name(participant.get('championId')),
                'champion_icon': self._get_champion_icon(participant.get('championName')),
                'champion_level': participant.get('champLevel'),

                # Position/Role
                'team_position': participant.get('teamPosition'),
                'individual_position': participant.get('individualPosition'),
                'role': participant.get('role'),
                'lane': participant.get('lane'),

                # KDA
                'kills': participant.get('kills', 0),
                'deaths': participant.get('deaths', 0),
                'assists': participant.get('assists', 0),
                'kda_ratio': self._calculate_kda(participant),

                # Damage
                'total_damage': participant.get('totalDamageDealtToChampions', 0),
                'physical_damage': participant.get('physicalDamageDealtToChampions', 0),
                'magic_damage': participant.get('magicDamageDealtToChampions', 0),
                'true_damage': participant.get('trueDamageDealtToChampions', 0),
                'damage_taken': participant.get('totalDamageTaken', 0),
                'damage_mitigated': participant.get('damageSelfMitigated', 0),

                # CS and Gold
                'cs': participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
                'cs_per_min': self._calculate_cs_per_min(participant, info.get('gameDuration')),
                'gold_earned': participant.get('goldEarned', 0),
                'gold_per_min': self._calculate_gold_per_min(participant, info.get('gameDuration')),

                # Vision
                'vision_score': participant.get('visionScore', 0),
                'wards_placed': participant.get('wardsPlaced', 0),
                'wards_killed': participant.get('wardsKilled', 0),
                'control_wards': participant.get('detectorWardsPlaced', 0),

                # Items
                'items': self._process_items(participant),
                'item_ids': [
                    participant.get(f'item{i}', 0) for i in range(7)
                ],

                # Summoner Spells
                'summoner_spells': self._process_summoner_spells(participant),
                'summoner1_id': participant.get('summoner1Id'),
                'summoner2_id': participant.get('summoner2Id'),

                # Runes
                'keystone': participant.get('perks', {}).get('styles', [{}])[0].get('selections', [{}])[0].get('perk'),
                'primary_rune_tree': participant.get('perks', {}).get('styles', [{}])[0].get('style'),
                'secondary_rune_tree': participant.get('perks', {}).get('styles', [{}])[1].get('style') if len(participant.get('perks', {}).get('styles', [])) > 1 else None,

                # Multi-kills
                'double_kills': participant.get('doubleKills', 0),
                'triple_kills': participant.get('tripleKills', 0),
                'quadra_kills': participant.get('quadraKills', 0),
                'penta_kills': participant.get('pentaKills', 0),

                # Objectives
                'turret_kills': participant.get('turretKills', 0),
                'inhibitor_kills': participant.get('inhibitorKills', 0),
                'baron_kills': participant.get('baronKills', 0),
                'dragon_kills': participant.get('dragonKills', 0),

                # Team data
                'team_id': participant.get('teamId'),
                'all_participants': all_participants['all'],
                'allies': all_participants['allies'],
                'enemies': all_participants['enemies'],

                # Additional stats
                'largest_killing_spree': participant.get('largestKillingSpree', 0),
                'largest_multi_kill': participant.get('largestMultiKill', 0),
                'killing_sprees': participant.get('killingSprees', 0),
                'time_ccing_others': participant.get('timeCCingOthers', 0),
                'total_heal': participant.get('totalHeal', 0),
                'total_healing_teammates': participant.get('totalHealsOnTeammates', 0),
                'damage_per_death': self._calculate_damage_per_death(participant),
                'kill_participation': self._calculate_kill_participation(participant, all_participants['allies']),

                # First blood/events
                'first_blood': participant.get('firstBloodKill', False),
                'first_blood_assist': participant.get('firstBloodAssist', False),
                'first_tower': participant.get('firstTowerKill', False),
                'first_tower_assist': participant.get('firstTowerAssist', False)
            }

            return processed

        except Exception as e:
            logger.error(f"Error processing match: {e}")
            return None

    def _find_participant(
        self,
        participants: List[Dict],
        puuid: str
    ) -> Optional[Dict]:
        """Find participant by PUUID."""
        for p in participants:
            if p.get('puuid') == puuid:
                return p
        return None

    def _process_all_participants(
        self,
        participants: List[Dict]
    ) -> Dict[str, List[Dict]]:
        """Process all participants into teams."""
        team_100 = []
        team_200 = []

        for p in participants:
            participant_data = {
                'puuid': p.get('puuid'),
                'summoner_name': p.get('riotIdGameName', p.get('summonerName', 'Unknown')),
                'summoner_tag': p.get('riotIdTagline', ''),
                'champion_id': p.get('championId'),
                'champion_name': self._get_champion_name(p.get('championId')),
                'champion_icon': self._get_champion_icon(p.get('championName')),
                'team_id': p.get('teamId'),
                'position': p.get('teamPosition'),
                'kills': p.get('kills', 0),
                'deaths': p.get('deaths', 0),
                'assists': p.get('assists', 0),
                'cs': p.get('totalMinionsKilled', 0) + p.get('neutralMinionsKilled', 0),
                'gold': p.get('goldEarned', 0),
                'damage': p.get('totalDamageDealtToChampions', 0),
                'win': p.get('win', False)
            }

            if p.get('teamId') == 100:
                team_100.append(participant_data)
            else:
                team_200.append(participant_data)

        # Sort by position
        position_order = ['TOP', 'JUNGLE', 'MIDDLE', 'BOTTOM', 'UTILITY']
        team_100.sort(key=lambda x: position_order.index(x['position']) if x['position'] in position_order else 99)
        team_200.sort(key=lambda x: position_order.index(x['position']) if x['position'] in position_order else 99)

        return {
            'all': participants,
            'allies': team_100,  # This will be corrected based on player's team
            'enemies': team_200
        }

    def _calculate_kda(self, participant: Dict) -> str:
        """Calculate KDA ratio."""
        kills = participant.get('kills', 0)
        deaths = participant.get('deaths', 0)
        assists = participant.get('assists', 0)

        if deaths == 0:
            return "Perfect" if kills + assists > 0 else "0.00"

        kda = (kills + assists) / deaths
        return f"{kda:.2f}"

    def _calculate_cs_per_min(self, participant: Dict, duration: int) -> float:
        """Calculate CS per minute."""
        if not duration or duration == 0:
            return 0.0

        cs = participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0)
        minutes = duration / 60
        return round(cs / minutes, 1)

    def _calculate_gold_per_min(self, participant: Dict, duration: int) -> float:
        """Calculate gold per minute."""
        if not duration or duration == 0:
            return 0.0

        gold = participant.get('goldEarned', 0)
        minutes = duration / 60
        return round(gold / minutes, 0)

    def _calculate_damage_per_death(self, participant: Dict) -> int:
        """Calculate damage per death."""
        deaths = participant.get('deaths', 0)
        damage = participant.get('totalDamageDealtToChampions', 0)

        if deaths == 0:
            return damage

        return round(damage / deaths)

    def _calculate_kill_participation(
        self,
        participant: Dict,
        allies: List[Dict]
    ) -> float:
        """Calculate kill participation percentage."""
        player_kp = participant.get('kills', 0) + participant.get('assists', 0)
        team_kills = sum(ally.get('kills', 0) for ally in allies)

        if team_kills == 0:
            return 0.0

        return round((player_kp / team_kills) * 100, 1)

    def _format_duration(self, seconds: int) -> str:
        """Format game duration."""
        if not seconds:
            return "0:00"

        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}:{remaining_seconds:02d}"

    def _calculate_time_ago(self, timestamp: int) -> str:
        """Calculate how long ago the game was."""
        if not timestamp:
            return "Unknown"

        game_time = datetime.fromtimestamp(timestamp / 1000)
        now = datetime.now()
        delta = now - game_time

        if delta.days > 30:
            months = delta.days // 30
            return f"{months}mo ago"
        elif delta.days > 0:
            return f"{delta.days}d ago"
        elif delta.seconds > 3600:
            hours = delta.seconds // 3600
            return f"{hours}h ago"
        elif delta.seconds > 60:
            minutes = delta.seconds // 60
            return f"{minutes}m ago"
        else:
            return "Just now"

    def _get_game_mode(self, mode: str) -> str:
        """Get readable game mode name."""
        mode_names = {
            'CLASSIC': 'Classic',
            'ARAM': 'ARAM',
            'TUTORIAL': 'Tutorial',
            'URF': 'URF',
            'NEXUSBLITZ': 'Nexus Blitz',
            'KINGPORO': 'King Poro',
            'ONEFORALL': 'One for All'
        }
        return mode_names.get(mode, mode)

    def _get_queue_type(self, queue_id: int) -> str:
        """Get readable queue type."""
        return QUEUES.get(queue_id, {}).get('description', 'Custom')

    def _get_champion_name(self, champion_id: int) -> str:
        """Get champion name by ID."""
        return CHAMPIONS.get(champion_id, {}).get('name', 'Unknown')

    def _get_champion_icon(self, champion_name: str) -> str:
        """Get champion icon URL."""
        if not champion_name:
            return '/static/img/champion/default.png'

        # Use Data Dragon CDN
        return f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/champion/{champion_name}.png"

    def _process_items(self, participant: Dict) -> List[Dict]:
        """Process item data."""
        items = []
        for i in range(7):
            item_id = participant.get(f'item{i}', 0)
            if item_id:
                item_data = ITEMS.get(item_id, {})
                items.append({
                    'id': item_id,
                    'name': item_data.get('name', 'Unknown Item'),
                    'icon': f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/item/{item_id}.png"
                })
            else:
                items.append(None)
        return items

    def _process_summoner_spells(self, participant: Dict) -> List[Dict]:
        """Process summoner spell data."""
        spells = []
        for spell_key in ['summoner1Id', 'summoner2Id']:
            spell_id = participant.get(spell_key)
            if spell_id:
                spell_data = SUMMONER_SPELLS.get(spell_id, {})
                spells.append({
                    'id': spell_id,
                    'name': spell_data.get('name', 'Unknown'),
                    'icon': f"https://ddragon.leagueoflegends.com/cdn/13.24.1/img/spell/{spell_data.get('key', 'SummonerFlash')}.png"
                })
        return spells