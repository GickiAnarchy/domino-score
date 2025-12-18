from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from datetime import datetime
import json
import os

SAVE_FILE = "players.json"
GAMES_FILE = "games.json"


# ======================
# DATA MODELS
# ======================
class Player:
	def __init__(self, name, wins=0, losses=0):
		self.name = name
		self.wins = wins
		self.losses = losses

	def to_dict(self):
		return {"name": self.name, "wins": self.wins, "losses": self.losses}

	@classmethod
	def from_dict(cls, data):
		return cls(**data)


class GameScore:
	def __init__(self, players):
		self.date = datetime.now()
		self.players = players
		self.scores = {p.name: 0 for p in players}

	def add_score(self, player_name, points):
		self.scores[player_name] += points

	def winner(self):
		return min(self.scores, key=self.scores.get)

	def to_dict(self):
		return {"date": self.date.isoformat(), "scores": self.scores}


# ======================
# SCREENS
# ======================
class MenuScreen(Screen):
	pass


class CreatePlayerScreen(Screen):
	def save_player(self, name):
		app = App.get_running_app()
		name = name.strip()

		if not name or name in app.players:
			Popup(
				title="Error",
				content=Label(text="Invalid or duplicate name"),
				size_hint=(0.7, 0.3),
			).open()
			return

		app.players[name] = Player(name)
		app.save_players()
		self.manager.current = "menu"


class PlayerSelectScreen(Screen):

	def on_enter(self):
		player_list = self.ids.player_list
		player_list.clear_widgets()

		app = App.get_running_app()
		for name in app.players:
			player_list.add_widget(ToggleButton(text=name, size_hint_y=None, height=50))


class GameScreen(Screen):

	def on_enter(self):
		scores_layout = self.ids.scores
		scores_layout.clear_widgets()

		app = App.get_running_app()
		game = app.current_game

		for player in game.players:
			row = BoxLayout(size_hint_y=None, height=50)

			row.add_widget(Label(text=player.name))

			score_input = TextInput(
				multiline=False, input_filter="int", hint_text="Points"
			)

			# bind without unsafe lambda capture
			score_input.bind(
				on_text_validate=self._make_score_handler(player.name, score_input)
			)

			row.add_widget(score_input)
			scores_layout.add_widget(row)

	def _make_score_handler(self, player_name, widget):
		def handler(instance):
			text = widget.text.strip()
			if text.isdigit():
				App.get_running_app().current_game.add_score(player_name, int(text))
				widget.text = ""

		return handler


class HistoryScreen(Screen):

	def on_enter(self):
		history_list = self.ids.history_list
		history_list.clear_widgets()

		app = App.get_running_app()

		if not os.path.exists(GAMES_FILE):
			history_list.add_widget(
				Label(text="No games played yet.", size_hint_y=None, height=40)
			)
			return

		with open(GAMES_FILE) as f:
			games = json.load(f)

		if not games:
			history_list.add_widget(
				Label(text="No games played yet.", size_hint_y=None, height=40)
			)
			return

		for game in reversed(games):  # newest first
			history_list.add_widget(self.build_game_row(game))

	def build_game_row(self, game):
		box = BoxLayout(orientation="vertical", size_hint_y=None, height=90, padding=10)
	
		date = datetime.fromisoformat(game["date"]).strftime("%Y-%m-%d %H:%M")
	
		scores = game["scores"]
		winner = max(scores, key=scores.get)
	
		box.add_widget(
			Label(text=f"[b]{date}[/b]", markup=True, size_hint_y=None, height=40)
		)
	
		score_text = ", ".join(f"{k}: {v}" for k, v in scores.items())
		box.add_widget(Label(text=score_text, size_hint_y=None, height=40))
	
		box.add_widget(Label(text=f"Winner: {winner}", size_hint_y=None, height=40, color = "red"))
	
		return box

# ======================
# APP
# ======================
class DominoApp(App):

	def build(self):
		self.players = self.load_players()
		self.current_game = None

		sm = ScreenManager()
		sm.add_widget(MenuScreen(name="menu"))
		sm.add_widget(CreatePlayerScreen(name="create"))
		sm.add_widget(PlayerSelectScreen(name="select"))
		sm.add_widget(GameScreen(name="game"))
		sm.add_widget(HistoryScreen(name="history"))
		return sm

	# ---------- Persistence ----------
	def load_players(self):
		if not os.path.exists(SAVE_FILE):
			return {}
		with open(SAVE_FILE) as f:
			data = json.load(f)
		return {k: Player.from_dict(v) for k, v in data.items()}

	def save_players(self):
		with open(SAVE_FILE, "w") as f:
			json.dump({k: v.to_dict() for k, v in self.players.items()}, f, indent=2)

	def save_game(self, game):
		games = []
		if os.path.exists(GAMES_FILE):
			with open(GAMES_FILE) as f:
				games = json.load(f)

		games.append(game.to_dict())

		with open(GAMES_FILE, "w") as f:
			json.dump(games, f, indent=2)

	# ---------- Game Flow ----------
	def start_game(self, names):
		if len(names) < 2:
			Popup(
				title="Select Players",
				content=Label(text="Select at least two players"),
				size_hint=(0.7, 0.3),
			).open()
			return
		else:
			players = [self.players[n] for n in names]
			self.current_game = GameScore(players)

	def finish_game(self):
		game = self.current_game
		winner = game.winner()

		for player in game.players:
			if player.name == winner:
				player.wins += 1
			else:
				player.losses += 1

		self.save_players()
		self.save_game(game)

		Popup(
			title="Game Over",
			content=Label(text=f"🏆 Winner: {winner}"),
			size_hint=(0.7, 0.3),
		).open()


# ======================
# RUN
# ======================
if __name__ == "__main__":
	DominoApp().run()
