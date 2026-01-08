import json
import logging
import os
import random
from datetime import datetime
from uuid import uuid4
#from android.permissions import request_permissions

from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.utils import get_color_from_hex, platform
from kivy.uix.screenmanager import ScreenManager
from kivymd.toast import toast

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
        format="%(asctime)s | %(levelname)s | %(message)s",)
    logging.info("=== App starting ===")

def ids_ready(screen, *names):
    return all(name in screen.ids for name in names)

def safe_load_json(path, default):
    if not path or not os.path.exists(path):
        return default
    try:
        if os.path.getsize(path) == 0:
            return default
    except Exception:
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        logging.exception(f"Failed to load JSON: {path}")
        return default

def atomic_write_json(path, data):
    tmp_path = f"{path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)  # atomic on Android/Linux
    except Exception:
        logging.exception(f"Failed atomic write: {path}")
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

def request_storage_permissions():
    if platform != "android":
        return

    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except Exception as e:
        logging.warning(f"Permission request skipped: {e}")

def get_data_dir():
    if platform == "android":
        from android.storage import app_storage_path
        return app_storage_path()
    return os.getcwd()


def get_export_dir():
    if platform == "android":
        try:
            from android.storage import primary_external_storage_path, app_storage_path
            base = primary_external_storage_path()
        except Exception:
            # Fallback to internal app storage (always safe)
            from android.storage import app_storage_path
            base = app_storage_path()
        path = os.path.join(base, "Download", "DominoScorebook")
    else:
        path = os.path.join(os.getcwd(), "exports")
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        path = os.getcwd()
    return path


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
    "Ready for a spanking?",
    "Too many doubles in your hand?\nYou might be able to call for\na redraw!",
    "Whoever leads the hand\nchooses how many dominoes \nto start with."
]

COLORS = [
    "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue",
    "LightBlue", "Cyan", "Teal", "Green", "LightGreen", "Lime",
    "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray", "BlueGray"]

THEME_BLK_RED = ["Black", "Red", "Gray"]


# --------------------------------------------------
# Models
# --------------------------------------------------

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
        self.ids.history_btn.disabled = not (
            GAMES_FILE and os.path.exists(GAMES_FILE))
        app = MDApp.get_running_app()
        self.ids.start_btn.disabled = not bool(app.players)
        self.ids.history_btn.disabled = not (
        GAMES_FILE is not None and os.path.exists(GAMES_FILE))
        

class OptionsScreen(MDScreen):
    def show_dialog(self, title, text):
        d = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: d.dismiss())])
        d.open()

    def export_saves(self):
        request_storage_permissions()
    
        app = MDApp.get_running_app()
        export_dir = get_export_dir()
    
        atomic_write_json(
            os.path.join(export_dir, "players.dom"),
            safe_load_json(SAVE_FILE, {})
        )
        atomic_write_json(
            os.path.join(export_dir, "games.dom"),
            safe_load_json(GAMES_FILE, [])
        )
    
        self.manager.current = "menu"

    def import_saves(self):
        app = MDApp.get_running_app()
        export_dir = get_export_dir()
    
        players_src = os.path.join(export_dir, "players.dom")
        games_src = os.path.join(export_dir, "games.dom")
        try:
            safe_load_json(players_src, "Player")
            toast("Imported players")      
            safe_load_json(games_src, "GameScore")
            toast("Imported Games")
        except Exception as e:
            print(e)
            return
        
        #if os.path.exists(players_src):
#            atomic_write_json(SAVE_FILE, safe_load_json(players_src, {}))
#    
#        if os.path.exists(games_src):
#            atomic_write_json(GAMES_FILE, safe_load_json(games_src, []))
    
        app.players = app.load_players()
        app.sync_players_from_games()
        self.manager.current = "menu"


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
            games = safe_load_json(GAMES_FILE, [])
            changed = False
            for g in games:
                if "id" not in g:
                    g["id"] = str(uuid4())
                    changed = True
            if changed:
                atomic_write_json(GAMES_FILE, games)
        except Exception:
            box.add_widget(MDLabel(text="Corrupted game history"))
            return
        for g in reversed(games):
            row = MDBoxLayout(orientation="horizontal", size_hint_y=None, height=dp(56))
            cb = HistoryCheckbox(size_hint=(None, None), size=(dp(48), dp(48)))
            cb.game_id = g.get("id")
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
        games = [g for g in games if g.get("id") not in self.selected]
        atomic_write_json(GAMES_FILE, games)
        self.on_enter()

    def edit_selected(self):
        self.selected.discard(None)
        if len(self.selected) != 1:
            return
        game_id = next(iter(self.selected))
        games = safe_load_json(GAMES_FILE, []) 
        for g in games:
            if g.get("id") == game_id:
                app = MDApp.get_running_app()
                game = GameScore([])
                game.id=g["id"]
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
            game.date = "Corrupted Date"
        game.totals = new_totals
        game.players = [Player(n) for n in new_totals.keys()]
        game.get_results()
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


class StatsScreen(MDScreen):
    pass


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

# ----------------------------------------------
# App
# ----------------------------------------------

class DominoApp(MDApp):
    def build(self):
        setup_logger()
        global DATA_DIR, SAVE_FILE, GAMES_FILE
        DATA_DIR = get_data_dir()
        os.makedirs(DATA_DIR, exist_ok=True)
        SAVE_FILE = os.path.join(DATA_DIR, "players.dom")
        GAMES_FILE = os.path.join(DATA_DIR, "games.dom")
        self.players = self.load_players()
        self.sync_players_from_games()
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
            (EditGameScreen,"edit"),
            (StatsScreen, "stats"),
        ]:
            sm.add_widget(cls(name=name))
        return sm
        
    def save_players(self):
        data = {
            "version": 1,
            "players": {
                name: {
                    "wins": player.wins,
                    "losses": player.losses,}
                for name, player in self.players.items()}}
        atomic_write_json(SAVE_FILE, data)
        
    def load_players(self):
        if not os.path.exists(SAVE_FILE):
            return {}    
        # Empty file guard
        if os.path.getsize(SAVE_FILE) == 0:
            logging.warning("Players save file is empty")
            return {}    
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            logging.error("Players save file contains invalid JSON")
            return {}
        except Exception:
            logging.exception("Unexpected error loading players")
            return {}    
        players_data = data.get("players")
        if not isinstance(players_data, dict):
            logging.error("Players save file has invalid schema")
            return {}    
        players = {}
        for name, stats in players_data.items():
            try:
                players[name] = Player(
                    name=name,
                    wins=int(stats.get("wins", 0)),
                    losses=int(stats.get("losses", 0)),)
            except Exception:
                logging.warning(f"Skipping invalid player entry: {name}")    
        return players

    def save_edited_game(self, edited_game):
        games = safe_load_json(GAMES_FILE, [])    
        # Replace game with same date
        replaced = False
        for i, g in enumerate(games):
            if g.get("id") == edited_game.id:
                games[i] = edited_game.to_dict()
                replaced = True
                break    
        # Fallback: append if not found
        if not replaced:
            games.append(edited_game.to_dict())    
        atomic_write_json(GAMES_FILE, games)    
        self.current_game = None
        self.root.current = "history"    
            
    def start_game(self, names):
        if not names or len(names) < 2:
            return    
        players = []
        for name in names:
            player = self.players.get(name)
            if player:
                players.append(player)    
        if len(players) < 2:
            logging.warning("Not enough valid players to start game")
            return    
        self.current_game = GameScore(players)        
        self.root.current = "game"

    def finish_game(self):
        game = self.current_game
        if not game:
            return    
        games1 = safe_load_json(GAMES_FILE, [])
        games = [g for g in games1 if g.get("id") != game.id]
        games.append(game.to_dict())
        atomic_write_json(GAMES_FILE, games)   
        self.current_game = None
        self.root.current = "menu"

    def compute_player_stats(self):
        stats = {}
        games = safe_load_json(GAMES_FILE, [])    
        for g in games:
            if not g.get("finished"):
                continue    
            winner = g.get("winner")
            if not winner:
                continue  
            for name in g.get("totals", {}):
                stats.setdefault(name, {"wins": 0, "losses": 0})   
            stats[winner]["wins"] += 1
            for name in g["totals"]:
                if name != winner:
                    stats[name]["losses"] += 1    
        return stats

    def sync_players_from_games(self):
        computed = self.compute_player_stats()
        for name, player in self.players.items():
            if name in computed:
                player.wins = computed[name]["wins"]
                player.losses = computed[name]["losses"]
            else:
                player.wins = 0
                player.losses = 0
    
    
    
    
if __name__ == "__main__":
    DominoApp().run()