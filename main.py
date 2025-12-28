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
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.utils import get_color_from_hex

import pickle
from datetime import datetime
import json
import os

SAVE_FILE = "players.json"
GAMES_FILE = "games.json"
UNFINISHED = ".unfinished.dom"
MAX_POINTS = 300
# --------------------------------------------------
SELECTED_COLOR = get_color_from_hex("#4CAF50")   # green
DEFAULT_COLOR  = get_color_from_hex("#1E88E5")   # blue


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
        if self.finished:
            return
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
    pass


class OptionsScreen(MDScreen):
    
    def reset_all(self):
        app = MDApp.get_running_app()
        app.players = []
        
        with open(GAMES_FILE, "w") as f:
            f.write("")
            f.close()
        with open(SAVE_FILE, "w") as f:
            f.write("")
            f.close()
        
        self.manager.current = "menu"


class CreatePlayerScreen(MDScreen):
    def save_player(self):
        app = MDApp.get_running_app()
        name = self.ids.player_name.text.strip()

        if not name or name in app.players:
            app.show_dialog("Error", "Invalid or duplicate name")
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
            
            #in_points = MDTextField()
            btncard = MDBoxLayout(orientation = "horizontal", size_hint = (0.9, None))

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

    def add(self, name, pts):
        app = MDApp.get_running_app()
        app.current_game.add_points(name, pts)
        self.refresh()

        if app.current_game.finished:
            app.finish_game()
            self.manager.current = "menu"


class HistoryScreen(MDScreen):
    selected = set()

    def on_enter(self):
        box = self.ids.history_list
        box.clear_widgets()
        self.selected.clear()
        

        if not os.path.exists(GAMES_FILE):
            box.add_widget(MDLabel(text="No games yet"))
            return
        
        games = []
        try:
            with open(GAMES_FILE) as f:
                games = json.load(f)
        except Exception as e:
            print(e)
            
        for g in reversed(games):
            row = MDBoxLayout(height=dp(80), size_hint_y=None)
            cb = MDCheckbox(
                on_active=lambda c, v, d=g["date"]: self.toggle(d, v)
            )
            row.add_widget(cb)
            row.add_widget(
                MDLabel(text=f'{g["date"][:16]} — {g["winner"]}')
            )
            box.add_widget(row)

    def toggle(self, game_id, value):
        if value:
            self.selected.add(game_id)
        else:
            self.selected.discard(game_id)

    def delete_selected(self):
        if not self.selected:
            return

        with open(GAMES_FILE) as f:
            games = json.load(f)

        games = [g for g in games if g["date"] not in self.selected]

        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

        self.on_enter()


# --------------------------------------------------
class DominoApp(MDApp):
    dialog = None

    def build(self):
        self.players = self.load_players()
        self.save_game_available = self.check_for_save()
        self.current_game = None

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Dark"

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
                print(f.read())
                if f.read() in [None, ""]:
                    return False
                else:
                    return True
        except:
            print('error loading')
            return
    
    def load_players(self):
        if not os.path.exists(SAVE_FILE):
            return {}
        with open(SAVE_FILE) as f:
            return {k: Player.from_dict(v) for k, v in json.load(f).items()}

    def save_players(self):
        with open(SAVE_FILE, "w") as f:
            json.dump({k: v.to_dict() for k, v in self.players.items()}, f, indent=2)

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
        winner = game.winner()
        
        if not game.finished:
            self.save_game()
            print("unfinished game saved")
            return

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
        games.append(game.to_dict())
        with open(GAMES_FILE, "w") as f:
            json.dump(games, f, indent=2)

        self.show_dialog("Game Over", f"Winner: {winner}")

if __name__ == "__main__":
    DominoApp().run()