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
