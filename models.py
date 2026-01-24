from datetime import datetime
from uuid import uuid4


class Player:

    def __init__(self, name, **kwargs):
        self.name = name  # Player name

        self.wins = kwargs.get("wins", 0)  # Total wins

        self.losses = kwargs.get("losses", 0)  # Total losses

        self.highest_score = kwargs.get(
            "highest_score", 0
        )  # Players highest score ever


    def reset_stats(self):
        self.wins = 0
        self.losses = 0


    def to_dict(self):
        p_dict = {
            "name": self.name,
            "wins": self.wins,
            "losses": self.losses,
            "highest_score": self.highest_score,
        }
        return p_dict

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data.get("name", ""),
            wins=data.get("wins", 0),
            losses=data.get("losses", 0),
            highest_score=data.get("highest_score", 0),
        )


class GameScore:

    def __init__(self, players, id=None, **kwargs):
        self.id = id or str(uuid4())  # Used to identify games.

        self.date = kwargs.get(
            "date", datetime.now().isoformat()
        )  # Keep in isoformat in file and in memory, only format to string to display

        self.players = list(players)  # List of [Player.name]'s

        self.totals = kwargs.get(
            "totals", {name: 0 for name in self.players}
        )  # dict: {player_name:score}

        self.finished = kwargs.get(
            "finished", False
        )  # Used to verify the game is closed and complete


    def finish_game(self):
        print("GameScore -> finish_game()")
        self.finished = True
        

    def add_points(self, name, points):
        if name not in self.totals:
            print(f"Player {name} is not in the game, it seems.")
        points = int(points)
        if points % 5 == 0:
            self.totals[name] += points
        else:
            print("Tried to add invalid value of points")


    def get_date(self) -> str:
        ddate = datetime.fromisoformat(self.date)
        data = f"{ddate:%m/%d/%y %I:%M%p}"
        return data


    @property
    def winner(self):
        high = max(self.totals.values())
        leaders = [name for name, score in self.totals.items() if score == high]
        # Tie → no winner yet
        if len(leaders) != 1:
            return None
        return leaders[0]


    def to_dict(self):
        return {
            "id": self.id,
            "date": self.date,
            "players": self.players,
            "totals": self.totals,
            "finished": self.finished,
        }


    @classmethod
    def from_dict(cls, data):
        return cls(
            players=data.get("players", []),
            id=data.get("id"),
            date=data.get("date"),
            totals=data.get("totals"),
            finished=data.get("finished", False),
        )
