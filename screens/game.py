from utils import *
from constants import *
from ui_helpers import *
from models import *
import logging

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
