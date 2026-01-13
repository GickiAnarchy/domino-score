from utils import *
from constants import *

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
    def show_dialog(self, title, text):
        d = MDDialog(
            title=title,
            text=text,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: d.dismiss())])
        d.open()

    def export_saves(self):
        app = MDApp.get_running_app()
        app.save_players()
        app.save_games()
        toast("Saves exported")
    
    def import_saves(self):
        app = MDApp.get_running_app()    
        players = load_players(app.players_file)
        games = load_games(app.games_file)
        if not players and not games:
            toast("No saves found")
            return  
        app.players = players
        app.games = games
        app.sync_players_from_games()
        toast("Saves imported")
        self.manager.current = "menu"