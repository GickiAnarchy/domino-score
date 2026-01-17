from datetime import datetime
from uuid import uuid4

from constants import MAX_POINTS


# ==========================================================
# PLAYER
# ==========================================================

class Player:
    def __init__(self, name, wins=0, losses=0):
        self.name = name
        self.wins = int(wins)
        self.losses = int(losses)

    def reset_stats(self):
        self.wins = 0
        self.losses = 0

    def to_dict(self):
        return {
            "name": self.name,
            "wins": self.wins,
            "losses": self.losses,}

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            wins=data.get("wins", 0),
            losses=data.get("losses", 0),)


# ==========================================================
# GAME SCORE
# ==========================================================

class GameScore:
    def __init__(self, players, id, **):
        self.id = id or str(uuid4())
        self.date = datetime.now().isoformat()
    
        self.players = list(players)
        self.totals = {p.name: 0 for p in self.players}
    
        self.rounds = []
        self.finished = False

    # ------------------------------------------------------
    # SCORING
    # ------------------------------------------------------

    
    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "totals": self.totals,
            "rounds": self.rounds,
            "finished": self.finished,
        }

    # ------------------------------------------------------

    @classmethod
    def from_dict(cls, data):
        game = cls(
            players=list(data.get("totals", {}).keys()),
            id=data.get("id"),
        )
    
        game.date = data.get("date", datetime.now().isoformat())
        game.totals = data.get("totals", {})
        game.rounds = data.get("rounds", [])
        game.finished = data.get("finished", False)
    
        return game