import json
import logging
import os
import random
import sys
from datetime import datetime

from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.uix.widget import Widget
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

# -------------------------------------------------- ()
# Logging & Paths
# --------------------------------------------------

def setup_logger():
    try:
        if platform == "android":
            from android.storage import primary_external_storage_path
            base = primary_external_storage_path()
            log_dir = os.path.join(base, "Download", "DominoScorebook")
        else:
            log_dir = os.path.join(os.getcwd(), "logs")

        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "domino.log")
    except Exception:
        log_file = os.path.join(os.getcwd(), "domino.log")

    logging.basicConfig(
        filename=log_file,
        filemode="a",
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )
    logging.info("=== App starting ===")
    return log_file


def get_data_dir():
    if platform == "android":
        from android.storage import app_storage_path
        print(app_storage_path())
        return app_storage_path()
    print(os.getcwd())
    return os.getcwd()


DATA_DIR = get_data_dir()

SAVE_FILE = os.path.join(DATA_DIR, "players.dom")
GAMES_FILE = os.path.join(DATA_DIR, "games.dom")
UNFINISHED = os.path.join(DATA_DIR, ".unfinished.dom")

MAX_POINTS = 300
SELECTED_COLOR = get_color_from_hex("#4CAF50")
DEFAULT_COLOR = get_color_from_hex("#1E88E5")

FACTS = ["All Hail King Dingle!!","Can you count to five?","Draw ya plenty of 'em.","Is it ridiculous yet?","The opponent can't make any points\noff the 2-3 domino.","Careful holding on\nto that Double-Six","Just a nickel at a time.","Eight, skate, and donate.","Niner, Not a tight vaginer", "Ready for a spanking?"]

COLORS = [
    "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue",
    "LightBlue", "Cyan", "Teal", "Green", "LightGreen", "Lime",
    "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray", "BlueGray"
]


def get_export_dir():
    if platform == "android":
        from android.storage import app_storage_path
        base = app_storage_path()
        export_dir = os.path.join(base, "exports")
    else:
        export_dir = os.path.join(os.getcwd(), "exports")

    os.makedirs(export_dir, exist_ok=True)
    return export_dir


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

    def winner(self):
        if not self.totals:
            return None
        if len(set(self.totals.values())) == 1:
            return "Tie Game"
        return max(self.totals, key=self.totals.get)

    def to_dict(self):
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
        self.md_bg_color = self.color


# --------------------------------------------------
# Screens
# --------------------------------------------------

class MenuScreen(MDScreen):

    def on_pre_enter(self,):
        self.update_labels()

    def on_enter(self):
        app = MDApp.get_running_app()
        self.ids.start_btn.disabled = not bool(app.players)
        self.ids.history_btn.disabled = not os.path.exists(GAMES_FILE)

    def update_labels(self):
        self.fact_label = self.ids.fact_label
        self.title_label = self.ids.title_label
        
        self.fact_label.text = random.choice(FACTS)


class OptionsScreen(MDScreen):
    def show_dialog(self, title, text):
        opt_dialig = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: opt_dialig.dismiss())],
        )
        opt_dialig.open()

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
            "Exported:\n" + "\n".join(exported) if exported else "Nothing to export"
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

        MDApp.get_running_app().players = MDApp.get_running_app().load_players()
        self.show_dialog("Import", "\n".join(imported) if imported else "Nothing imported")


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
        if not app.current_game:
            return

        box = self.ids.player_container
        box.clear_widgets()

        for name, score in app.current_game.totals.items():
            top = MDBoxLayout(orientation="horizontal", size_hint=(0.9, None), height=dp(40))
            top.add_widget(MDLabel(text=f"{name} — {score}", font_style="H6"))

            btns = MDBoxLayout(spacing=dp(15), size_hint=(0.9, None), height=dp(50))
            for pts in (5, 10, 20, -5):
                btns.add_widget(
                    MDRaisedButton(
                        text=f"{pts:+}",
                        on_release=lambda x, n=name, p=pts: self.add(n, p),
                    )
                )

            box.add_widget(top)
            box.add_widget(btns)
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
            date = g.get("date", "Unknown")
            winner = g.get("winner", "In Progress")
            totals = g.get("totals", {})

            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
            cb = HistoryCheckbox(size_hint=(None, None), size=(dp(48), dp(48)))
            cb.game_id = date
            cb.bind(active=self.on_checkbox)
            row.add_widget(cb)

            col = MDBoxLayout(orientation="vertical")
            col.add_widget(MDLabel(text=f"{date[:16]} — {winner}"))
            col.add_widget(MDLabel(text=str(totals), font_style="Caption"))
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


# --------------------------------------------------
# Main App Class
# --------------------------------------------------

class DominoApp(MDApp):
    def build(self):
        setup_logger()
        os.makedirs(DATA_DIR, exist_ok=True)

        self.players = self.load_players()
        self.current_game = None

        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.accent_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"

        try:
            LabelBase.register(name="BreakAway", fn_regular="data/breakaway.ttf")
        except Exception as e:
            logging.warning(f"Font not found: {e}")

        sm = ScreenManager()
        screens = [
            (MenuScreen, "menu"),
            (CreatePlayerScreen, "create"),
            (PlayerSelectScreen, "select"),
            (GameScreen, "game"),
            (HistoryScreen, "history"),
            (OptionsScreen, "options"),
        ]
        for cls, name in screens:
            sm.add_widget(cls(name=name))

        return sm

    def save_players(self):
        tmp = SAVE_FILE + ".tmp"
        try:
            with open(tmp, "w") as f:
                json.dump({k: v.to_dict() for k, v in self.players.items()}, f, indent=2)
            os.replace(tmp, SAVE_FILE)
        except Exception as e:
            logging.error(f"Failed to save players: {e}")

    def load_players(self):
        if not os.path.exists(SAVE_FILE):
            return {}
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            return {k: Player.from_dict(v) for k, v in data.items()}
        except Exception as e:
            logging.error(f"Failed to load players: {e}")
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
            try:
                with open(GAMES_FILE) as f:
                    games = json.load(f)
            except Exception:
                pass

        games.append(game.to_dict())
        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

        self.current_game = None
        self.root.current = "menu"


if __name__ == "__main__":
    DominoApp().run()
