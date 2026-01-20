from utils import *
from constants import *
from ui_helpers import ConfirmDialog

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




class OptionsScreen(MDScreen):
    
    def reset_players(self):
        
        def do_reset():
            self.app.reset_players()
        
        self.reset_confirm = ConfirmDialog(title="Reset Confirmation", text="This will reset ALL players!\nAre you sure?", on_confirm=do_reset,)
        self.reset_confirm.open()

    
    @property
    def app(self):
        return MDApp.get_running_app()