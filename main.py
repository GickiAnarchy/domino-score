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
from kivy.clock import Clock
from kivy.utils import platform
from kivy.utils import get_color_from_hex
from kivymd.uix.fitimage import FitImage
from kivy.core.text import LabelBase
from kivy.utils import platform

import pickle
import random
from functools import partial
from datetime import datetime
import json
import os


def get_data_dir():
    if platform == "android":
        from android.storage import app_storage_path
        return app_storage_path()
    return os.getcwd()

DATA_DIR = get_data_dir()

SAVE_FILE = os.path.join(DATA_DIR, "players.json")
GAMES_FILE = os.path.join(DATA_DIR, "games.json")
UNFINISHED = os.path.join(DATA_DIR, ".unfinished.dom")
MAX_POINTS = 300
# --------------------------------------------------
SELECTED_COLOR = get_color_from_hex("#4CAF50")   # green
DEFAULT_COLOR  = get_color_from_hex("#1E88E5")   # blue

# Quotes, Facts, Etc.
FACTS = ["All Hail King Dingle!!","Can you count to five?","Draw ya plenty of 'em.","Is it ridiculous yet?","The opponent can't\nmake any points\noff the 2-3 domino.","Careful holding on\nto that Double-Six","Just a nickel at a time.","Eight, skate, and donate.","Niner, Not a right vaginer"]

COLORS = ["Red","Pink","Purple","DeepPurple","Indigo","Blue","LightBlue","Cyan","Teal","Green","LightGreen","Lime","Yellow","Amber","Orange","DeepOrange","Brown","Gray","BlueGray"]


def get_export_dir():
    if platform == "android":
        from android.storage import app_storage_path
        base = app_storage_path()
        export_dir = os.path.join(base, "exports")
    else:
        export_dir = os.path.join(os.getcwd(), "exports")

    os.makedirs(export_dir, exist_ok=True)
    return export_dir

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
        self.date = datetime.now()
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
            "date": self.date.isoformat(),
            "totals": self.totals,
            "winner": self.winner(),
            "finished": self.finished,
        }

    @classmethod
    def from_dict(cls, data):
        return cls(**data)


# --------------------------------------------------
class MenuScreen(MDScreen):
     
     def on_enter(self):
        app = MDApp.get_running_app()

        has_players = bool(app.players)
        has_games = os.path.exists(GAMES_FILE)

        self.ids.start_btn.disabled = not has_players
        #self.ids.stats_btn.disabled = not has_players
        self.ids.history_btn.disabled = not has_games
     
     def has_unfinished(self):
         return os.path.exists(UNFINISHED)
     
     def get_fact(self):
         return random.choice(FACTS)
     
     
class MDSeparator(MDBoxLayout):
    thickness = NumericProperty(dp(1))
    color = ListProperty([1, 1, 1, 0.2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = self.thickness
        self.md_bg_color = self.color

        # react to property changes
        self.bind(thickness=self._update_height)
        self.bind(color=self._update_color)

    def _update_height(self, *args):
        self.height = self.thickness

    def _update_color(self, *args):
        self.md_bg_color = self.color
    
 
class OptionsScreen(MDScreen):
    confirm_dialog = None

    def show_confirm_reset(self):
        if self.confirm_dialog:
            self.confirm_dialog.dismiss()

        self.confirm_dialog = MDDialog(
            title="Reset All Data?",
            text=(
                "This will permanently delete:\n\n"
                "• All players\n"
                "• All game history\n\n"
                "This action cannot be undone."
            ),
            buttons=[
                MDFlatButton(
                    text="CANCEL",
                    on_release=lambda x: self.confirm_dialog.dismiss(),
                ),
                MDFlatButton(
                    text="RESET",
                    text_color=(1, 0, 0, 1),  # red warning
                    on_release=lambda x: self.confirm_reset(),
                ),
            ],
        )
        self.confirm_dialog.open()
    
    def confirm_reset(self):
        self.confirm_dialog.dismiss()
        self.reset_all()
    
    def show_dialog(self, title, text):
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()

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
            
        self.show_dialog("Export Complete", msg)

    def import_saves(self):
        import_dir = get_export_dir()
    
        if not os.path.exists(import_dir):
            self.show_dialog("Import Failed", "No backup folder found")
            return
    
        imported = []
    
        for fname in [".players.dom", ".games.dom"]:
            src = os.path.join(import_dir, fname)
            dst = os.path.join(get_data_dir(), fname)
    
            if os.path.exists(src):
                with open(src, "r") as s, open(dst, "w") as d:
                    d.write(s.read())
                imported.append(fname)
    
        msg = (
            "Imported:\n" + "\n".join(imported)
            if imported else
            "No valid save files found."
        )
    
        self.show_dialog("Imported", msg)
    
        app = MDApp.get_running_app()
        app.players = app.load_players()
    
    def reset_all(self):
        app = MDApp.get_running_app()
        app.players = {}
    
        for fname in (SAVE_FILE, GAMES_FILE):
            try:
                if os.path.exists(fname):
                    os.remove(fname)
            except Exception as e:
                print(f"Failed to delete {fname}: {e}")
    
        self.manager.current = "menu"
    

class CreatePlayerScreen(MDScreen):
    def save_player(self):
        app = MDApp.get_running_app()
        name = self.ids.player_name.text.strip()

        if not name or name in app.players:
            MDDialog(
                title="Error",
                text="Invalid or duplicate name",
                buttons=[
                    MDFlatButton(text="OK", on_release=lambda x: x.parent.parent.dismiss())
                ],
            ).open()
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
            chip = MDRaisedButton(
                text=name,
                on_release=lambda x, n=name: self.toggle(n, x),
            )
            box.add_widget(chip)

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
    
    def end_pressed(self):
        app = MDApp.get_running_app()
        app.finish_game()
        self.manager.current = "menu"

    def refresh(self):
        box = self.ids.player_container
        box.clear_widgets()
        app = MDApp.get_running_app()

        for name, score in app.current_game.totals.items():
            card = MDCard(
                orientation="vertical",
                padding=dp(10),
                size_hint_y=None,
                height=dp(120),
            )
            topcard = MDBoxLayout(orientation="horizontal", size_hint = (0.9, None))
            
            topcard.add_widget(
                MDLabel(text=f"{name} — {score}", font_style="H6")
            )
            
            btncard = MDBoxLayout(orientation = "horizontal", size_hint = (0.9, None), spacing=dp(15), pos_hint={"center_x":0.5})

            btn5 = MDRaisedButton(
                text="+5",
                on_release=lambda x, n=name: self.add(n, 5),
            )
            btn10 = MDRaisedButton(
                text="+10",
                on_release=lambda x, n=name: self.add(n, 10),
            )
            btn20 = MDRaisedButton(
                text="+20",
                on_release=lambda x, n=name: self.add(n, 20),
            )
            btnm5 = MDRaisedButton(
                text="-5",
                on_release=lambda x, n=name: self.add(n, -5),
            )
            btncard.add_widget(btn5)
            btncard.add_widget(btn10)
            btncard.add_widget(btn20)
            btncard.add_widget(btnm5)
            box.add_widget(topcard)
            box.add_widget(btncard)
            box.add_widget(MDSeparator(thickness = dp(5)))

    def add(self, name, pts):
        app = MDApp.get_running_app()
        app.current_game.add_points(name, pts)
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
            with open(GAMES_FILE, "r") as f:
                games = json.load(f)
        except Exception as e:
            print("❌ Failed to load games.json:", e)
            box.add_widget(MDLabel(text="Corrupted game history"))
            return

        for g in reversed(games):
            try:
                # ---- validate required fields ----
                date = g.get("date", "Unknown date")
                winner = g.get("winner", "In Progress")
                totals = g.get("totals", {})

                row = MDBoxLayout(
                    orientation="horizontal",
                    height=dp(56),
                    spacing=dp(12),
                    size_hint_y=None,
                )

                cb = HistoryCheckbox(size_hint=(0.3, 0.3))
                cb.game_id = date
                cb.bind(active=self.on_checkbox_active)

                b = MDBoxLayout(orientation="vertical")

                label = MDLabel(
                    text=f"{date[:16]} — {winner}",
                    valign="middle",
                )

                label2 = MDLabel(
                    text=str(totals),
                    valign="middle",
                )

                b.add_widget(label)
                b.add_widget(label2)

                row.add_widget(cb)
                row.add_widget(b)
                box.add_widget(row)

            except Exception as e:
                # ---- THIS is Fix #3 ----
                print("⚠️ Skipping bad game entry:", e)
                continue
            
    def on_checkbox_active(self, checkbox, value):
        game_id = checkbox.game_id
    
        if value:
            self.selected.add(game_id)
            print(game_id, "added")
        else:
            self.selected.discard(game_id)
            print(game_id, "removed")
        
        #def toggle(self, game_id, checkbox, value):
#            if value:
#                self.selected.add(game_id)
#                print(game_id + " added")
#            else:
#                self.selected.discard(game_id)
#                print(game_id + " removed")

    def delete_selected(self):
        if not self.selected:
            print("None selected?")
            return
        
        print(self.selected)

        with open(GAMES_FILE) as f:
            games = json.load(f)
            f.close()

        games = [g for g in games if g["date"] not in self.selected]

        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)
            f.close()

        self.on_enter()


# --------------------------------------------------
class DominoApp(MDApp):
    dialog = None

    def build(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        self.players = self.load_players()
        self.save_game_available = self.check_for_save()
        self.current_game = None
        

        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.accent_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"
        
        LabelBase.register(
            name="BreakAway",
            fn_regular="data/breakaway.ttf"
        )
        
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(CreatePlayerScreen(name="create"))
        sm.add_widget(PlayerSelectScreen(name="select"))
        sm.add_widget(GameScreen(name="game"))
        sm.add_widget(HistoryScreen(name="history"))
        sm.add_widget(OptionsScreen(name="options"))
        return sm

    # ---------- helpers ----------
    def show_dialog(self, title, text):
        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()

    # ---------- persistence ----------
    def check_for_save(self):
        try:
            with open(UNFINISHED, "rb") as f:
                data = f.read()
                return bool(data)
        except Exception:
            return False
    
    def load_players(self):
        if not os.path.exists(SAVE_FILE):
            return {}
    
        try:
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
    
            if not isinstance(data, dict):
                raise ValueError("players.json is not a dict")
    
            return {k: Player.from_dict(v) for k, v in data.items()}
    
        except Exception as e:
            print("❌ Failed to load players:", e)
    
            # BACKUP the bad file so the app can recover
            try:
                os.rename(SAVE_FILE, SAVE_FILE + ".corrupt")
            except Exception:
                pass
    
            return {}

    def save_game(self):
        with open(UNFINISHED, "wb") as f:
            pickle.dump(self.current_game, f)

    def reload_game(self):
        unfinished_game = None
        if not os.path.exists(UNFINISHED):
            return
        with open(UNFINISHED, "rb") as f:
            try:
                self.current_game = pickle.load(f)
            except EOFError as e:
                print(e)
                f.close()
                os.remove(UNFINISHED)
                return
            f.close()
        open(UNFINISHED, "wb").close()
        self.root.current = "game"

    # ---------- game flow ----------
    def start_game(self, names):
        if len(names) < 2:
            if self.save_game_available:
                self.reload_game()
                return
            self.show_dialog("Error", "Select at least two players")
            return

        self.current_game = GameScore([self.players[n] for n in names])
        self.root.current = "game"

    def finish_game(self):
        game = self.current_game
        winner = None
        
        if not game.finished:
            self.show_confirm("Unfinished Game","Do you want to save this game?", on_yes=self.save_game, on_no=lambda: None)
            return
        else:
            winner = game.winner()

        if winner not in ("Tie Game", None):
            for p in game.players:
                if p.name == winner:
                    p.wins += 1
                else:
                    p.losses += 1

        self.save_players()

        games = []
        if os.path.exists(GAMES_FILE):
            with open(GAMES_FILE) as f:
                games = json.load(f)
        game_data = game.to_dict()

        # ensure required keys always exist
        game_data.setdefault("totals", {})
        game_data.setdefault("winner", None)
        game_data.setdefault("rounds", [])
        game_data.setdefault("finished", False)
        
        games.append(game_data)
        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

        self.show_dialog("Game Over", f"Winner: {winner}")
    
    def show_confirm(self, title, text, on_yes, on_no):
        confirm_dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="No",
                    on_release=lambda x: (
                        confirm_dialog.dismiss(),
                        on_no()
                    ),
                ),
                MDFlatButton(
                    text="Yes",
                    text_color=(1, 0, 0, 1),
                    on_release=lambda x: (
                        confirm_dialog.dismiss(),
                        on_yes()
                    ),
                ),
            ],
        )
        confirm_dialog.open()


if __name__ == "__main__":
    DominoApp().run()