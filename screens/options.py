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
        request_storage_permissions()
    
        app = MDApp.get_running_app()
        export_dir = get_export_dir()
    
        atomic_write_json(
            os.path.join(export_dir, "players.dom"),
            safe_load_json(SAVE_FILE, {})
        )
        atomic_write_json(
            os.path.join(export_dir, "games.dom"),
            safe_load_json(GAMES_FILE, [])
        )
    
        self.manager.current = "menu"

    def import_saves(self):
        app = MDApp.get_running_app()
        export_dir = get_export_dir()
    
        players_src = os.path.join(export_dir, "players.dom")
        games_src = os.path.join(export_dir, "games.dom")
        try:
            safe_load_json(players_src, "Player")
            toast("Imported players")      
            safe_load_json(games_src, "GameScore")
            toast("Imported Games")
        except Exception as e:
            print(e)
            return
        
        #if os.path.exists(players_src):
#            atomic_write_json(SAVE_FILE, safe_load_json(players_src, {}))
#    
#        if os.path.exists(games_src):
#            atomic_write_json(GAMES_FILE, safe_load_json(games_src, []))
    
        app.players = app.load_players()
        app.sync_players_from_games()
        self.manager.current = "menu"

