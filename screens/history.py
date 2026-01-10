from utils import *
from constants import *
from ui_helpers import *
from models import *

from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.utils import platform
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

