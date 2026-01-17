from datetime import datetime
from uuid import uuid4


# ==========================================================
# PLAYER
# ==========================================================

class Player:
    def __init__(self, name, **kwargs):
        self.name = name
        self.wins = kwargs.get("wins",0)
        self.losses = kwargs.get("losses",0)

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


#. ==========================================================
# GAME SCORE
# ==========================================================

class GameScore:
    def __init__(self, players, id=None, **kwargs):
        self.id = id or str(uuid4())
        # Use existing date if passed via kwargs, else now
        self.date = kwargs.get("date", datetime.now().isoformat())    
        # 1. Store only the names (Strings)
        # This allows you to look up the Player object from your app's main list
        self.players = list(players)         
        # 2. Initialize totals based on names
        self.totals = kwargs.get("totals", {name: 0 for name in self.players})
        self.finished = kwargs.get("finished", False)


    def finish_game(self):
        self.finished = True
    
    
    def add_points(self, name, points):
        if name not in self.totals:
            print(f"Player {name} is not in the game, it seems.")
        points = int(points)
        self.totals[name] += points


    @property
    def winner(self):
        if not self.finished or not self.totals:
            return None    
        high = max(self.totals.values())
        leaders = [name for name, score in self.totals.items() if score == high]        
        # Tie → no winner yet
        if len(leaders) != 1:
            return None            
        return leaders[0]


    def to_dict(self):
        """Converts the game object into a dictionary for JSON/Pickle saving"""
        return {
            "id": self.id,
            "date": self.date,
            "players": self.players,  # This is your list of names: ["Alice", "Bob"]
            "totals": self.totals,
            "finished": self.finished,}


    @classmethod
    def from_dict(cls, data):
        """Creates a GameScore object from a dictionary"""
        # Pass data through kwargs to the __init__
        return cls(
            players=data.get("players", []),
            id=data.get("id"),
            date=data.get("date"),
            totals=data.get("totals"),
            finished=data.get("finished", False))