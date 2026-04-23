from __future__ import annotations
import asyncio
import time
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from api import QueuedPlayer


class QueuedPlayer:
    def __init__(self, username: str, elo: int, join_time: float):
        self.username = username
        self.elo = elo
        self.join_time = join_time


class RankedQueue:
    def __init__(self):
        self.queue: list[QueuedPlayer] = []
        self.lock = asyncio.Lock()
        
        # Phase configuration: (player_count, elo_range, duration_seconds)
        self.phases = [
            (6, 50, 30),   # 6 players, +/- 50 ELO, for 30 seconds
            (6, 100, 30),   # 6 players, +/- 100 ELO, for 30 more seconds
            (4, 50, 30),   # 4 players,  +/- 50 ELO, for 30 more seconds
            (4, 100, 30),   # 4 players, +/- 100 ELO, for 30 more seconds
            (3, 50, 30),   # 3 players, +/- 500 ELO, for 30 more seconds
            (2, 50, 30),   # 2 players, +/- 50 ELO, for 30 more seconds
            (2, 100, None),  # 2 players, +/- 100 ELO, indefinitely
        ]
    
    async def add_player(self, username: str, elo: int) -> None:
        async with self.lock:
            self.queue.append(QueuedPlayer(username, elo, time.time()))
            # Keep sorted by ELO for efficient matching
            self.queue.sort(key=lambda p: p.elo)
    
    async def remove_player(self, username: str) -> bool:
        """Remove player if they cancel queue. Returns True if found."""
        async with self.lock:
            for i, player in enumerate(self.queue):
                if player.username == username:
                    self.queue.pop(i)
                    return True
        return False
    
    def _get_phase(self, wait_time: float) -> tuple[int, int]:
        """
        Determine phase based on wait time.
        Returns (required_players, elo_range)
        """
        elapsed = 0
        for required_players, elo_range, duration in self.phases:
            if duration is None or wait_time < elapsed + duration:
                return required_players, elo_range
            elapsed += duration
        # Fallback to last phase
        return self.phases[-1][0], self.phases[-1][1]
    
    async def try_match(self) -> Optional[list[str]]:
        """
        Try to form a match based on current queue state.
        Returns list of matched usernames or None.
        """
        async with self.lock:
            if not self.queue:
                return None
            
            # Get the player who's been waiting longest
            oldest_player = self.queue[0]
            wait_time = time.time() - oldest_player.join_time
            required_players, elo_range = self._get_phase(wait_time)
            
            # Find similar ELO players
            candidates = []
            for player in self.queue:
                if abs(player.elo - oldest_player.elo) <= elo_range:
                    candidates.append(player)
                    if len(candidates) == required_players:
                        break
            
            # Match found
            if len(candidates) == required_players:
                matched_names = [p.username for p in candidates]
                # Remove matched players from queue
                self.queue = [p for p in self.queue if p.username not in matched_names]
                return matched_names
        
        return None
