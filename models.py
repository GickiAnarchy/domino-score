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
            "losses": self.losses,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            wins=data.get("wins", 0),
            losses=data.get("losses", 0),
        )


# ==========================================================
# GAME SCORE
# ==========================================================

class GameScore:
    def __init__(self, players, id=None):
        self.id = id or str(uuid4())
        self.date = datetime.now().isoformat()

        self.players = players
        self.totals = {p.name: 0 for p in players}

        self.rounds = []
        self.finished = False   # explicit only

    # ------------------------------------------------------
    # SCORING
    # ------------------------------------------------------

    def add_points(self, name, pts):
        if self.finished:
            return

        if name not in self.totals:
            return

        pts = int(pts)
        self.totals[name] += pts

        self.rounds.append({
            "player": name,
            "points": pts,
        })

    # ------------------------------------------------------
    # PROVISIONAL STATE
    # ------------------------------------------------------

    @property
    def provisional_leader(self):
        """
        Player currently leading (may or may not have reached MAX_POINTS)
        """
        if not self.totals:
            return None

        return max(self.totals.items(), key=lambda x: x[1])[0]

    @property
    def max_reached(self):
        """
        True if someone has reached or exceeded MAX_POINTS
        (does NOT end the game)
        """
        return any(score >= MAX_POINTS for score in self.totals.values())

    # ------------------------------------------------------
    # FINAL GAME STATE
    # ------------------------------------------------------

    def finish(self):
        """
        Called at the end of the hand.
        Locks the game and finalizes the winner.
        """
        self.finished = True

    @property
    def winner(self):
        """
        Final winner — ONLY valid after finish()
        """
        if not self.finished or not self.totals:
            return None

        return max(self.totals.items(), key=lambda x: x[1])[0]

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
        game = cls(players=[], id=data.get("id"))

        game.date = data.get("date", datetime.now().isoformat())
        game.totals = data.get("totals", {})
        game.rounds = data.get("rounds", [])
        game.finished = data.get("finished", False)

        game.players = [Player(name) for name in game.totals.keys()]

        return game