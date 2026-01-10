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