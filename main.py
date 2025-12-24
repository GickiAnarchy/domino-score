from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserIconView
from kivy.metrics import dp
from kivy.animation import Animation
from kivy.clock import Clock
import shutil
from datetime import datetime
import json
import os

SAVE_FILE = "players.json"
GAMES_FILE = "games.json"


def get_export_dir():
    try:
        # Android
        from android.storage import primary_external_storage_path

        base = primary_external_storage_path()
        return os.path.join(base, "Download", "DominoScorebook")
    except Exception:
        # Desktop fallback
        return os.path.join(os.getcwd(), "exports")


MAX_POINTS = 300  # configurable win condition


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
        self.rounds = []
        self.totals = {p.name: 0 for p in players}
        self.undo_stack = []
        self.finished = False

    def add_points(self, player_name, points):
        if self.finished:
            return

        self.totals[player_name] += points
        self.undo_stack.append((player_name, points))

        self.rounds.append(
            {
                "player": player_name,
                "points": points,
                "time": datetime.now().isoformat(),
            }
        )

    def undo_last(self):
        if not self.undo_stack:
            return
        player, points = self.undo_stack.pop()
        self.totals[player] -= points
        self.rounds.pop()

    def winner(self):
        if len(set(self.totals.values())) == 1:
            return "Tie Game"
        return max(self.totals, key=self.totals.get)

    def check_game_over(self):
        for score in self.totals.values():
            if score <= MAX_POINTS:
                self.finished = False
                return False
        self.finished = True
        return True

    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "rounds": self.rounds,
            "totals": self.totals,
            "winner": self.winner(),
            "finished": self.finished,
        }


# ======================
# SCREENS
# ======================
class SplashScreen(Screen):

    def on_enter(self):
        logo = self.ids.logo
        loading = self.ids.loading

        # Reset state (important if screen reused)
        logo.opacity = 0
        logo.scale = 0.9
        loading.opacity = 0

        # Logo fade + scale
        logo_anim = Animation(opacity=1, scale=1, duration=3, t="out_quad")

        # Loading text pulse
        loading_anim = Animation(opacity=1, duration=0.3) + Animation(
            opacity=0.3, duration=0.4
        )
        loading_anim.repeat = True

        loading_anim.start(loading)
        logo_anim.start(logo)

        # Move to menu after splash
        Clock.schedule_once(self.go_to_menu, 5.5)

    def go_to_menu(self, *args):
        self.manager.current = "menu"


class OptionsScreen(Screen):

    def export_saves(self):
        export_dir = get_export_dir()
        os.makedirs(export_dir, exist_ok=True)

        files = [SAVE_FILE, GAMES_FILE]
        exported = []

        for fname in files:
            if os.path.exists(fname):
                dest = os.path.join(export_dir, fname)
                with open(fname, "r") as src, open(dest, "w") as dst:
                    dst.write(src.read())
                exported.append(fname)

        if exported:
            msg = "Exported:\n" + "\n".join(exported) + "\n\nLocation:\n" + export_dir
        else:
            msg = "Nothing to export yet."

        Popup(
            title="Export Complete",
            content=Label(text=msg),
            size_hint=(0.8, 0.5),
        ).open()

    def import_saves(self):
        import_dir = get_export_dir()

        if not os.path.exists(import_dir):
            Popup(
                title="Import Failed",
                content=Label(text="No backup folder found."),
                size_hint=(0.7, 0.3),
            ).open()
            return

        imported = []

        for fname in [SAVE_FILE, GAMES_FILE]:
            src = os.path.join(import_dir, fname)
            if os.path.exists(src):
                with open(src, "r") as s, open(fname, "w") as d:
                    d.write(s.read())
                imported.append(fname)

        if imported:
            msg = "Imported:\n" + "\n".join(imported)
        else:
            msg = "No valid save files found."

        Popup(
            title="Import Complete",
            content=Label(text=msg),
            size_hint=(0.7, 0.4),
        ).open()

        # Reload players immediately
        app = App.get_running_app()
        app.players = app.load_players()


class AboutScreen(Screen):
    pass


class MenuScreen(Screen):
    pass


class StatsScreen(Screen):

    def on_enter(self):
        container = self.ids.stats_list
        container.clear_widgets()

        app = App.get_running_app()

        for player in app.players.values():
            btn = Button(text=f"{player.name}", size_hint_y=None, height=50)
            btn.bind(on_release=lambda _, p=player: self.show_player_stats(p))
            container.add_widget(btn)

    def show_player_stats(self, player):
        app = App.get_running_app()

        # calculate extra stats if you want
        total_games = player.wins + player.losses
        win_rate = (player.wins / total_games * 100) if total_games else 0

        content = BoxLayout(orientation="vertical", padding=15, spacing=10)

        content.add_widget(Label(text=f"[b]{player.name}[/b]", markup=True))
        content.add_widget(Label(text=f"Wins: {player.wins}"))
        content.add_widget(Label(text=f"Losses: {player.losses}"))
        content.add_widget(Label(text=f"Games Played: {total_games}"))
        content.add_widget(Label(text=f"Win Rate: {win_rate:.1f}%"))

        close_btn = Button(text="Close", size_hint_y=None, height=40)
        content.add_widget(close_btn)

        popup = Popup(
            title="Player Stats",
            content=content,
            size_hint=(0.75, 0.6),
            auto_dismiss=False,
        )

        close_btn.bind(on_release=popup.dismiss)
        popup.open()


class CreatePlayerScreen(Screen):

    def save_player(self, name):
        app = App.get_running_app()
        name = name.strip()
        name_input = self.ids.player_name_input

        if not name or name in app.players:
            Popup(
                title="Error",
                content=Label(text="Invalid or duplicate name"),
                size_hint=(0.7, 0.3),
            ).open()
            return

        app.players[name] = Player(name)
        app.save_players()
        name_input.text = ""
        self.manager.current = "menu"


class PlayerSelectScreen(Screen):

    def on_enter(self):
        player_list = self.ids.player_list
        player_list.clear_widgets()

        app = App.get_running_app()
        for name in app.players:
            player_list.add_widget(ToggleButton(text=name, size_hint_y=None, height=75))


class GameScreen(Screen):

    def on_enter(self):
        self.refresh_ui()

    def refresh_ui(self):
        container = self.ids.player_container
        container.clear_widgets()

        app = App.get_running_app()
        game = app.current_game

        for player in game.players:
            container.add_widget(self.build_player_card(player.name))

    def build_player_card(self, name):
        app = App.get_running_app()
        game = app.current_game

        card = BoxLayout(
            orientation="vertical", size_hint_y=0.4, padding=10, spacing=15
        )

        # card = BoxLayout(
        # 			orientation="vertical", size_hint_y=None, height=254, padding=10, spacing=15
        # 		)

        score_label = Label(
            text=f"{name} — Score: {game.totals[name]}", size_hint_y=None, font_size = "26sp")
        
		

        def update_label():
            score_label.text = f"{name} — Score: {game.totals[name]}"

        btn_row = BoxLayout(size_hint_y=0.4, spacing=10, padding=10)

        btn5 = Button(text="+5", size_hint_y=0.8)
        btn10 = Button(text="+10", size_hint_y=0.8)
        btnmin5 = Button(text="-5", size_hint_y=0.8)

        # 		btn5 = Button(text="+5", height=dp(65), size_hint_y=None)
        # 		btn10 = Button(text="+10", height=dp(65), size_hint_y=None)
        # 		btnmin5 = Button(text="-5", height=dp(65), size_hint_y = None)

        btn5.bind(on_release=lambda *_: self.add_score(name, 5, update_label))
        btn10.bind(on_release=lambda *_: self.add_score(name, 10, update_label))
        btnmin5.bind(on_release=lambda *_: self.add_score(name, -5, update_label))

        btn_row.add_widget(btn5)
        btn_row.add_widget(btn10)
        btn_row.add_widget(btnmin5)

        input_box = TextInput(
            multiline=False,
            input_filter="int",
            hint_text="Enter points",
            size_hint_y=0.3,
        )

        input_box.bind(
            on_text_validate=lambda instance: self.add_score(
                name, int(instance.text), update_label, instance
            )
        )

        card.add_widget(score_label)
        card.add_widget(btn_row)
        card.add_widget(input_box)

        return card

    def add_score(self, name, points, refresh_cb, input_widget=None):
        app = App.get_running_app()
        game = app.current_game

        game.add_points(name, points)
        if input_widget:
            input_widget.text = ""

        refresh_cb()

        if game.check_game_over():
            app.finish_game()
            self.manager.current = "menu"

    def end_game(self, in_widget=None):
        app = App.get_running_app()
        app.finish_game()
        self.manager.current = "menu"


class HistoryScreen(Screen):

    def on_enter(self):
        history_list = self.ids.history_list
        history_list.clear_widgets()
        games = []

        if not os.path.exists(GAMES_FILE):
            history_list.add_widget(Label(text="No games played yet."))
            return

        with open(GAMES_FILE) as f:
            try:
                games = json.load(f)
            except Exception as e:
                print(f"oops: {e}")

        # print(type(games[0] or None))

        try:
            for game in reversed(games):
                history_list.add_widget(self.build_game_row(game))
        except Exception as e:
            print(f"oops : {e}")

    def build_game_row(self, game):
        box = BoxLayout(orientation="vertical", size_hint_y=None, height=110)

        date = datetime.fromisoformat(game["date"]).strftime("%Y-%m-%d %H:%M")
        winner = game.get("winner", "Unknown")
        totals = game.get("totals", {})

        score_text = ", ".join(f"{k}: {v}" for k, v in totals.items())

        box.add_widget(Label(text=f"[b]{date}[/b]", markup=True))
        box.add_widget(Label(text=score_text))
        box.add_widget(Label(text=f"Winner: {winner}"))

        return box


# ======================
# APP
# ======================
class DominoApp(App):

    def build(self):
        self.players = self.load_players()
        self.current_game = None

        sm = ScreenManager()
        sm.add_widget(SplashScreen(name="splash"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(CreatePlayerScreen(name="create"))
        sm.add_widget(PlayerSelectScreen(name="select"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(StatsScreen(name="stats"))
        sm.add_widget(AboutScreen(name="about"))
        sm.add_widget(OptionsScreen(name="options"))
        sm.current = "splash"

        Clock.schedule_once(self.post_build_init, 0)

        return sm

    def post_build_init(self, *args):
        self.players = self.load_players()

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
            try:
                with open(GAMES_FILE) as f:
                    games = json.load(f)
            except Exception as e:
                print(f"oops line 291: {e}")

        try:
            games.append(game.to_dict())
        except Exception as ee:
            print(f"ooops line 296: {ee}")

        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

    # ---------- Game Flow ----------()
    def start_game(self, names):
        if len(names) < 2:
            Popup(
                title="Select Players",
                content=Label(text="Select at least two players"),
                size_hint=(0.7, 0.3),
            ).open()
            return

        players = [self.players[n] for n in names]
        self.current_game = GameScore(players)
        self.root.current = "game"

    def finish_game(self):
        game = self.current_game
        winner = game.winner()

        if winner != "Tie Game":
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
