import json
import logging
import os
import random
from datetime import datetime
from android.permissions import request_permissions

from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.utils import get_color_from_hex, platform
from kivy.uix.screenmanager import ScreenManager

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivymd.uix.textfield import MDTextField


# --------------------------------------------------
# Paths & Logging (SAFE)
# --------------------------------------------------




def ids_ready(screen, *names):
    return all(name in screen.ids for name in names)


  
      
DATA_DIR = None
SAVE_FILE = None
GAMES_FILE = None

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
    "Ready for a spanking?"
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
        self.finished = any(total >= MAX_POINTS for total in self.totals.values())

    def winner(self):
        if not self.totals:
            return None
        if not self.finished:
            return None
        return max(self.totals.items(), key=lambda x: x[1])[0]
        
    def to_dict(self):
        return {
            "date": self.date,
            "totals": self.totals,
            "winner": self.winner(),
            "finished": self.finished,}


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
        if not ids_ready(self, "fact_label", "start_btn", "history_btn"):
            return
        self.ids.fact_label.text = random.choice(FACTS)
        app = MDApp.get_running_app()
        self.ids.start_btn.disabled = not bool(app.players)
        #self.ids.history_btn.disabled = not (
            #GAMES_FILE and os.path.exists(GAMES_FILE)
        )
        app = MDApp.get_running_app()
        self.ids.start_btn.disabled = not bool(app.players)
        self.ids.history_btn.disabled = not (
        #GAMES_FILE is not None and os.path.exists(GAMES_FILE))
        

class OptionsScreen(MDScreen):
    def show_dialog(self, title, text):
        d = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: d.dismiss())])
        d.open()

    def export_saves(self):
        pass

    def import_saves(self):
        pass


class HistoryCheckbox(MDCheckbox):
    game_id = None


class HistoryScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.selected = set()

    def on_enter(self):
        if not ids_ready(self, "history_list"):
            return
        
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
        game_id = checkbox.game_id
        if not game_id:
            return
    
        if value:
            self.selected.add(game_id)
        else:
            self.selected.discard(game_id)
        
    def delete_selected(self):
        self.selected.discard(None)
        if not self.selected:
            return

        games = safe_load_json(GAMES_FILE, [])

        games = [g for g in games if g.get("date") not in self.selected]

        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

        self.on_enter()

    def edit_selected(self):
        self.selected.discard(None)
        if len(self.selected) != 1:
            return

        game_id = next(iter(self.selected))

        games = safe_load_json(GAMES_FILE, []) 

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
        app = MDApp.get_running_app()
        if not app.current_game:
            self.manager.current = "history"
            return  
        self.populate()
    
    def populate(self):
        app = MDApp.get_running_app()
        if not ids_ready(self, "score_table", "date_field"):
            return
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
            input_filter="int",)
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
        app.save_edited_game(game)

    def cancel(self):
        self.manager.current = "history"


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
        if not ids_ready(self, "player_list"):
            return
        box = self.ids.player_list
        box.clear_widgets()

        for name in MDApp.get_running_app().players:
            btn = MDRaisedButton(
                text=name,
                on_release=lambda x, n=name: self.toggle(n, x),)
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
        if not ids_ready(self, "player_container"):
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
                        on_release=lambda x, n=name, p=pts: self.add(n, p),))
            box.add_widget(top)
            box.add_widget(btns)
            box.add_widget(MDSeparator(thickness=dp(5)))

    def add(self, name, pts):
        app = MDApp.get_running_app()
        if not app.current_game:
            logging.warning("Attempted to score with no active game")
            return    
        app.current_game.add_points(name, pts)
        self.refresh()

# --------------------------------------------------
# App
# --------------------------------------------------

class DominoApp(MDApp):
    def build(self):
        setup_logger()
        global DATA_DIR, SAVE_FILE, GAMES_FILE
        DATA_DIR = get_export_dir()
        os.makedirs(DATA_DIR, exist_ok=True)
        SAVE_FILE = os.path.join(DATA_DIR, "players.dom")
        GAMES_FILE = os.path.join(DATA_DIR, "games.dom")
        self.players = self.load_players()
        self.current_game = None
        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"
        font_path = os.path.join(os.path.dirname(__file__), "data", "breakaway.ttf")
        if os.path.exists(font_path):
            try:
                LabelBase.register(
                    name="BreakAway",
                    fn_regular=font_path
                )
            except Exception:
                logging.exception("Failed to register BreakAway font")
        else:
            logging.warning("BreakAway font not found, using default")
        sm = ScreenManager()
        for cls, name in [
            (MenuScreen, "menu"),
            (CreatePlayerScreen, "create"),
            (PlayerSelectScreen, "select"),
            (GameScreen, "game"),
            (OptionsScreen, "options"),
            (HistoryScreen,"history"),
            (EditGameScreen,"edit"),]:
            sm.add_widget(cls(name=name))
        return sm
        
    

    def finish_game(self):
        game = self.current_game
        if not game:
            return
        games = safe_load_json(GAMES_FILE, [])
        games = [g for g in games if g.get("date") != game.date]
        games.append(game.to_dict())
        atomic_write_json(GAMES_FILE, games)
        self.current_game = None
        self.root.current = "menu"


if __name__ == "__main__":
    DominoApp().run()