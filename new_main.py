import json
import os
import sys
import uuid
import random
import logging
from datetime import datetime

from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.gridlayout import MDGridLayout
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivy.uix.screenmanager import ScreenManager
from kivy.properties import NumericProperty, ListProperty
from kivy.metrics import dp
from kivy.utils import platform, get_color_from_hex
from kivy.core.text import LabelBase

# -------------------- paths & logging --------------------

def get_data_dir():
    if platform == "android":
        from android.storage import app_storage_path
        return app_storage_path()
    return os.getcwd()

DATA_DIR = get_data_dir()
SAVE_FILE = os.path.join(DATA_DIR, "players.json")
GAMES_FILE = os.path.join(DATA_DIR, "games.json")
UNFINISHED = os.path.join(DATA_DIR, "unfinished.json")
MAX_POINTS = 300

SELECTED_COLOR = get_color_from_hex("#4CAF50")
DEFAULT_COLOR = get_color_from_hex("#1E88E5")

FACTS = [
    "All Hail King Dingle!!",
    "Can you count to five?",
    "Draw ya plenty of 'em.",
]

COLORS = ["Red", "Pink", "Purple", "Indigo", "Blue", "Green", "Orange", "Gray"]

def setup_logger():
    log_file = os.path.join(DATA_DIR, "domino.log")
    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logging.info("=== App start ===")

# -------------------- helpers --------------------

def get_export_dir():
    base = DATA_DIR
    export_dir = os.path.join(base, "exports")
    os.makedirs(export_dir, exist_ok=True)
    return export_dir

# -------------------- models --------------------

class Player:
    def __init__(self, name, wins=0, losses=0):
        self.name = name
        self.wins = wins
        self.losses = losses

    def to_dict(self):
        return {"name": self.name, "wins": self.wins, "losses": self.losses}

    @classmethod
    def from_dict(cls, d):
        return cls(d["name"], d.get("wins", 0), d.get("losses", 0))

class GameScore:
    def __init__(self, players):
        self.uid = str(uuid.uuid4())
        self.date = datetime.now().isoformat()
        self.players = players
        self.totals = {p.name: 0 for p in players}
        self.rounds = []
        self.finished = False

    def add_points(self, name, pts):
        self.totals[name] += pts
        self.rounds.append({"player": name, "points": pts})
        if self.totals[name] >= MAX_POINTS:
            self.finished = True

    def winner(self):
        if len(set(self.totals.values())) == 1:
            return "Tie Game"
        return max(self.totals, key=self.totals.get)

    def to_dict(self):
        return {
            "uid": self.uid,
            "date": self.date,
            "totals": self.totals,
            "rounds": self.rounds,
            "winner": self.winner(),
            "finished": self.finished,
        }

    @classmethod
    def from_dict(cls, d):
        obj = cls([])
        obj.uid = d.get("uid")
        obj.date = d.get("date")
        obj.totals = d.get("totals", {})
        obj.rounds = d.get("rounds", [])
        obj.finished = d.get("finished", False)
        return obj

# -------------------- UI widgets --------------------

class MDSeparator(MDBoxLayout):
    thickness = NumericProperty(dp(1))
    color = ListProperty([1, 1, 1, 0.2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = self.thickness
        self.md_bg_color = self.color

# -------------------- screens --------------------

class MenuScreen(MDScreen):
    def on_enter(self):
        app = MDApp.get_running_app()
        app.save_game_available = app.check_for_save()
        self.ids.start_btn.disabled = not bool(app.players)
        # Note: Added safety check for history button
        if hasattr(self.ids, 'history_btn'):
            self.ids.history_btn.disabled = not os.path.exists(GAMES_FILE)

    def get_fact(self):
        return random.choice(FACTS)

class OptionsScreen(MDScreen):
    def export_saves(self):
        export_dir = get_export_dir()
        exported = []
        for src in (SAVE_FILE, GAMES_FILE):
            if os.path.exists(src):
                dst = os.path.join(export_dir, os.path.basename(src))
                with open(src, "r") as fsrc, open(dst, "w") as fdst:
                    fdst.write(fsrc.read())
                exported.append(os.path.basename(src))
        self.show_dialog("Export", "\n".join(exported) or "Nothing to export")

    def import_saves(self):
        import_dir = get_export_dir()
        for name in ("players.json", "games.json"):
            src = os.path.join(import_dir, name)
            dst = os.path.join(DATA_DIR, name)
            if os.path.exists(src):
                with open(src, "r") as fsrc, open(dst, "w") as fdst:
                    fdst.write(fsrc.read())
        
        app = MDApp.get_running_app()
        app.players = app.load_players()
        self.show_dialog("Import", "Import complete")

    def show_dialog(self, title, text):
        MDDialog(
            title=title, 
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: x.parent.parent.dismiss())]
        ).open()

class CreatePlayerScreen(MDScreen):
    def save_player(self):
        app = MDApp.get_running_app()
        name = self.ids.player_name.text.strip()
        if not name or name in app.players:
            return
        app.players[name] = Player(name)
        app.save_players()
        self.ids.player_name.text = ""
        self.manager.current = "menu"

class PlayerSelectScreen(MDScreen):
    selected = set()

    def on_enter(self):
        self.selected.clear()
        box = self.ids.player_list
        box.clear_widgets()
        app = MDApp.get_running_app()
        for name in app.players:
            btn = MDRaisedButton(
                text=name,
                on_release=lambda x, n=name: self.toggle(n, x)
            )
            box.add_widget(btn)

    def toggle(self, name, btn):
        if name in self.selected:
            self.selected.remove(name)
            btn.md_bg_color = DEFAULT_COLOR
        else:
            self.selected.add(name)
            btn.md_bg_color = SELECTED_COLOR

    def start(self):
        MDApp.get_running_app().start_game(list(self.selected))

class GameScreen(MDScreen):
    def on_enter(self):
        self.refresh()

    def refresh(self):
        box = self.ids.player_container
        box.clear_widgets()
        app = MDApp.get_running_app()
        for name, score in app.current_game.totals.items():
            card = MDCard(orientation="vertical", padding=dp(10), size_hint_y=None, height=dp(150))
            card.add_widget(MDLabel(text=f"{name} — {score}", font_style="H6"))
            btns = MDBoxLayout(spacing=dp(10))
            for pts in (5, 10, 20, -5):
                btns.add_widget(MDRaisedButton(text=str(pts), on_release=lambda x, n=name, p=pts: self.add(n, p)))
            card.add_widget(btns)
            box.add_widget(card)
            box.add_widget(MDSeparator())

    def add(self, name, pts):
        MDApp.get_running_app().current_game.add_points(name, pts)
        self.refresh()

class HistoryCheckbox(MDCheckbox):
    uid = None

class HistoryScreen(MDScreen):
    def on_enter(self):
        box = self.ids.history_list
        box.clear_widgets()
        if not os.path.exists(GAMES_FILE):
            box.add_widget(MDLabel(text="No games yet"))
            return
        with open(GAMES_FILE) as f:
            games = json.load(f)
        for g in reversed(games):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
            cb = HistoryCheckbox(size_hint=(None, None), size=(dp(48), dp(48)))
            cb.uid = g.get("uid")
            row.add_widget(cb)
            row.add_widget(MDLabel(text=f"{g.get('date', '')[:16]} — {g.get('winner')}"))
            box.add_widget(row)

# -------------------- app --------------------

class DominoApp(MDApp):
    def build(self):
        setup_logger()
        os.makedirs(DATA_DIR, exist_ok=True)
        self.players = self.load_players()
        self.current_game = None
        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"
        
        # Note: Ensure you have the font file in the correct path or comment this out
        try:
            LabelBase.register(name="BreakAway", fn_regular="data/breakaway.ttf")
        except Exception as e:
            logging.error(f"Could not load font: {e}")

        sm = ScreenManager()
        screens = [
            (MenuScreen, "menu"),
            (CreatePlayerScreen, "create"),
            (PlayerSelectScreen, "select"),
            (GameScreen, "game"),
            (HistoryScreen, "history"),
            (OptionsScreen, "options")
        ]
        for screen_class, name in screens:
            sm.add_widget(screen_class(name=name))
        return sm

    def save_players(self):
        with open(SAVE_FILE, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.players.items()}, f, indent=2)

    def load_players(self):
        if not os.path.exists(SAVE_FILE):
            return {}
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            return {k: Player.from_dict(v) for k, v in data.items()}
        except Exception:
            return {}

    def check_for_save(self):
        return os.path.exists(UNFINISHED)

    def start_game(self, names):
        if len(names) < 2:
            return
        self.current_game = GameScore([self.players[n] for n in names])
        self.root.current = "game"

    def finish_game(self):
        game = self.current_game
        games = []
        if os.path.exists(GAMES_FILE):
            with open(GAMES_FILE) as f:
                games = json.load(f)
        games.append(game.to_dict())
        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)
        self.root.current = "menu"

if __name__ == "__main__":
    DominoApp().run()
