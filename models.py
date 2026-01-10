from datetime import datetime
import json
from uuid import uuid4

from constants import MAX_POINTS


class Player:
    def __init__(self, name, wins=0, losses=0):
        self.name = name
        self.wins = wins
        self.losses = losses
    
    def reset_stats(self):
        self.wins = 0
        self.losses = 0

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class GameScore:
    def __init__(self, players, id = None):
        self.id = id or str(uuid4())
        self.date = datetime.now().isoformat()
        self.players = players
        self.totals = {p.name: 0 for p in players}
        self.rounds = []
        self.finished = False

    def add_points(self, name, pts):
        self.totals[name] += pts
        self.rounds.append({"player": name, "points": pts})
        self.finished = any(total >= MAX_POINTS for total in self.totals.values())

    def winner(self):
        if not self.totals:
            return None
        if not self.finished:
            return None
        return max(self.totals.items(), key=lambda x: x[1])[0]
        
    def check_finished(self):
        """Return True if any player has reached MAX_POINTS"""
        return any(score >= MAX_POINTS for score in self.totals.values())
    
    def get_results(self):
        """
        Returns:
            {"finished": bool,
             "winner": [names],
             "losers": [names],
             "high_score": int}
        """
        if not self.totals:
            return None
        finished = self.check_finished()
        if not finished:
            return {
                "finished": False,
                "winner": None,
                "losers": [],
                "high_score": None,}    
        high_score = max(self.totals.values())
        winner = max(self.totals.items(), key=lambda x: x[1])[0]
        losers = [name for name in self.totals if name != winner]        
        return {
            "finished": True,
            "winner": winner,
            "losers": losers,
            "high_score": high_score,}
    
    def to_dict(self):
        results = self.get_results()
        return {
            "id": self.id,
            "date": self.date,
            "totals": self.totals,
            "finished": results["finished"] if results else False,
            "winner": results["winner"] if results else None,
            "losers": results["losers"] if results else [],}
