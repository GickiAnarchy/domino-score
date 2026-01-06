import json
import logging
import os
import random
from datetime import datetime

from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.utils import get_color_from_hex, platform
from kivy.uix.screenmanager import ScreenManager

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.card import MDCard
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.textfield import MDTextField


# --------------------------------------------------
# Paths & Logging (SAFE)
# --------------------------------------------------

DATA_DIR = None
SAVE_FILE = None
GAMES_FILE = None
UNFINISHED = None


def setup_logger():
    try:
        if platform == "android":
            from android.storage import app_storage_path
            base = app_storage_path()
        else:
            base = os.getcwd()

        log_dir = os.path.join(base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "domino.log")
    except Exception:
        log_file = "domino.log"

    logging.basicConfig(
        filename=log_file,
        filemode="a",
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logging.info("=== App starting ===")


def get_data_dir():
    if platform == "android":
        from android.storage import app_storage_path
        return app_storage_path()
    return os.getcwd()


def get_export_dir():
    if platform == "android":
        from android.storage import primary_external_storage_path
        base = primary_external_storage_path()
        path = os.path.join(base, "Download", "DominoScorebook")
    else:
        path = os.path.join(os.getcwd(), "exports")

    os.makedirs(path, exist_ok=True)
    return path


# --------------------------------------------------
# Constants
# --------------------------------------------------

MAX_POINTS = 300
SELECTED_COLOR = get_color_from_hex("#4CAF50")
DEFAULT_COLOR = get_color_from_hex("#1E88E5")

FACTS = [
    "All Hail King Dingle!!",
    "Can you count to five?",
    "Draw ya plenty of 'em.",
    "Is it ridiculous yet?",
    "The opponent can't make any points\noff the 2-3 domino.",
    "Careful holding on\nto that Double-Six",
    "Just a nickel at a time.",
    "Eight, skate, and donate.",
    "Niner, Not a tight vaginer",
    "Ready for a spanking?",
]

COLORS = [
    "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue",
    "LightBlue", "Cyan", "Teal", "Green", "LightGreen", "Lime",
    "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray", "BlueGray"
]


# --------------------------------------------------
# Models
# --------------------------------------------------

class Player:
    def __init__(self, name, wins=0, losses=0):
        self.name = name
        self.wins = wins
        self.losses = losses

    def to_dict(self):
        return self.__dict__

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


class GameScore:
    def __init__(self, players):
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

    def check_finished(self):
        self.finished = any(v >= MAX_POINTS for v in self.totals.values())

    def winner(self):
        if not self.finished:
            return None
        if len(set(self.totals.values())) == 1:
            return "Tie Game"
        return max(self.totals, key=self.totals.get)

    def to_dict(self):
        self.check_finished()
        return {
            "date": self.date,
            "totals": self.totals,
            "winner": self.winner(),
            "finished": self.finished,
        }


# --------------------------------------------------
# UI Helpers
# --------------------------------------------------

class MDSeparator(MDBoxLayout):
    thickness = NumericProperty(dp(1))
    color = ListProperty([1, 1, 1, 0.2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = self.thickness
        self.md_bg_color = [1, 1, 1, 0.2]


# --------------------------------------------------
# Screens
# --------------------------------------------------

class MenuScreen(MDScreen):
    def on_enter(self):
        self.ids.fact_label.text = random.choice(FACTS)
        app = MDApp.get_running_app()
        self.ids.start_btn.disabled = not bool(app.players)
        self.ids.history_btn.disabled = not os.path.exists(GAMES_FILE)


class OptionsScreen(MDScreen):
    def show_dialog(self, title, text):
        d = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: d.dismiss())],
        )
        d.open()

    def export_saves(self):
        export_dir = get_export_dir()
        exported = []

        for src in (SAVE_FILE, GAMES_FILE):
            if os.path.exists(src):
                dst = os.path.join(export_dir, os.path.basename(src))
                with open(src, "r") as s, open(dst, "w") as d:
                    d.write(s.read())
                exported.append(os.path.basename(src))

        self.show_dialog(
            "Export Complete",
            "\n".join(exported) if exported else "Nothing to export",
        )

    def import_saves(self):
        import_dir = get_export_dir()
        imported = []

        for name in ("players.dom", "games.dom"):
            src = os.path.join(import_dir, name)
            dst = os.path.join(DATA_DIR, name)
            if os.path.exists(src):
                with open(src, "r") as s, open(dst, "w") as d:
                    d.write(s.read())
                imported.append(name)

        app = MDApp.get_running_app()
        app.players = app.load_players()

        self.show_dialog(
            "Import Complete",
            "\n".join(imported) if imported else "Nothing imported",
        )


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
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected = set()

    def on_enter(self):
        self.selected.clear()
        box = self.ids.player_list
        box.clear_widgets()

        for name in MDApp.get_running_app().players:
            btn = MDRaisedButton(
                text=name,
                on_release=lambda x, n=name: self.toggle(n, x),
            )
            box.add_widget(btn)

    def toggle(self, name, button):
        if name in self.selected:
            self.selected.remove(name)
            button.md_bg_color = DEFAULT_COLOR
        else:
            self.selected.add(name)
            button.md_bg_color = SELECTED_COLOR

    def start(self):
        MDApp.get_running_app().start_game(list(self.selected))


class GameScreen(MDScreen):
    def on_enter(self):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        game = app.current_game
        if not game:
            return

        box = self.ids.player_container
        box.clear_widgets()

        for name, score in game.totals.items():
            row = MDBoxLayout(orientation="horizontal", spacing=dp(10))
            row.add_widget(MDLabel(text=f"{name} — {score}", font_style="H6"))

            for pts in (5, 10, 20, -5):
                row.add_widget(
                    MDRaisedButton(
                        text=f"{pts:+}",
                        on_release=lambda x, n=name, p=pts: self.add(n, p),
                    )
                )

            box.add_widget(row)
            box.add_widget(MDSeparator(thickness=dp(5)))

    def add(self, name, pts):
        MDApp.get_running_app().current_game.add_points(name, pts)
        self.refresh()


class HistoryCheckbox(MDCheckbox):
    game_id = None


class HistoryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected = set()

    def on_enter(self):
        box = self.ids.history_list
        box.clear_widgets()
        self.selected.clear()

        if not os.path.exists(GAMES_FILE):
            box.add_widget(MDLabel(text="No games yet"))
            return

        try:
            with open(GAMES_FILE) as f:
                games = json.load(f)
        except Exception:
            box.add_widget(MDLabel(text="Corrupted game history"))
            return

        for g in reversed(games):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
            cb = HistoryCheckbox(size_hint=(None, None), size=(dp(48), dp(48)))
            cb.game_id = g.get("date")
            cb.bind(active=self.on_checkbox)
            row.add_widget(cb)

            col = MDBoxLayout(orientation="vertical")
            col.add_widget(MDLabel(text=f"{g.get('date')[:16]} — {g.get('winner')}"))
            col.add_widget(MDLabel(text=str(g.get('totals')), font_style="Caption"))
            row.add_widget(col)
            box.add_widget(row)

    def on_checkbox(self, checkbox, value):
        if value:
            self.selected.add(checkbox.game_id)
        else:
            self.selected.discard(checkbox.game_id)

    def delete_selected(self):
        if not self.selected:
            return

        with open(GAMES_FILE) as f:
            games = json.load(f)

        games = [g for g in games if g.get("date") not in self.selected]

        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

        self.on_enter()

    def edit_selected(self):
        if len(self.selected) != 1:
            return

        game_id = next(iter(self.selected))

        with open(GAMES_FILE) as f:
            games = json.load(f)

        for g in games:
            if g.get("date") == game_id:
                app = MDApp.get_running_app()
                game = GameScore([])
                game.date = g["date"]
                game.totals = g["totals"]
                game.finished = g.get("finished", False)
                game.players = [Player(n) for n in g["totals"].keys()]
                app.current_game = game
                self.manager.current = "edit"
                return


class EditGameScreen(MDScreen):
    def on_pre_enter(self):
        self.populate()

    def populate(self):
        app = MDApp.get_running_app()
        table = self.ids.score_table
        table.clear_widgets()

        game = app.current_game
        if not game:
            return

        self.ids.date_field.text = game.date

        for name, score in game.totals.items():
            self.add_row(name, score)

    def add_row(self, name="", score=0):
        row = MDBoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))

        name_field = MDTextField(text=name, hint_text="Player", mode="rectangle")
        score_field = MDTextField(
            text=str(score),
            hint_text="Score",
            mode="rectangle",
            input_filter="int",
        )

        row.name_field = name_field
        row.score_field = score_field

        row.add_widget(name_field)
        row.add_widget(score_field)
        self.ids.score_table.add_widget(row)

    def save_game(self):
        app = MDApp.get_running_app()
        game = app.current_game
        if not game:
            return

        new_totals = {}

        for row in self.ids.score_table.children:
            name = row.name_field.text.strip()
            score = row.score_field.text.strip()
            if not name:
                continue
            try:
                new_totals[name] = int(score)
            except ValueError:
                new_totals[name] = 0

        if not new_totals:
            return

        try:
            game.date = datetime.fromisoformat(self.ids.date_field.text).isoformat()
        except ValueError:
            game.date = datetime.now().isoformat()

        game.totals = new_totals
        game.players = [Player(n) for n in new_totals.keys()]
        app.finish_game()

    def cancel(self):
        self.manager.current = "history"


# --------------------------------------------------
# App
# --------------------------------------------------

class DominoApp(MDApp):
    def build(self):
        setup_logger()

        global DATA_DIR, SAVE_FILE, GAMES_FILE, UNFINISHED
        DATA_DIR = get_data_dir()
        os.makedirs(DATA_DIR, exist_ok=True)

        SAVE_FILE = os.path.join(DATA_DIR, "players.dom")
        GAMES_FILE = os.path.join(DATA_DIR, "games.dom")
        UNFINISHED = os.path.join(DATA_DIR, ".unfinished.dom")

        self.players = self.load_players()
        self.current_game = None

        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"

        try:
            LabelBase.register(name="BreakAway", fn_regular="data/breakaway.ttf")
        except Exception:
            pass

        sm = ScreenManager()
        for cls, name in [
            (MenuScreen, "menu"),
            (CreatePlayerScreen, "create"),
            (PlayerSelectScreen, "select"),
            (GameScreen, "game"),
            (HistoryScreen, "history"),
            (OptionsScreen, "options"),
            (EditGameScreen, "edit"),
        ]:
            sm.add_widget(cls(name=name))

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

    def start_game(self, names):
        if len(names) < 2:
            return
        self.current_game = GameScore([self.players[n] for n in names])
        self.root.current = "game"

    def finish_game(self):
        game = self.current_game
        if not game:
            return

        games = []
        if os.path.exists(GAMES_FILE):
            with open(GAMES_FILE) as f:
                games = json.load(f)

        games = [g for g in games if g.get("date") != game.date]
        games.append(game.to_dict())

        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

        self.current_game = None
        self.root.current = "menu"


if __name__ == "__main__":
    DominoApp().run()