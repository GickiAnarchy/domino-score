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

