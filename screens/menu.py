from utils import *
from constants import *
import os

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





class MenuScreen(MDScreen):
    def on_enter(self):
        GAMES_FILE = MDApp.get_running_app().games_file
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
        