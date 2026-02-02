import os
import logging
import json
import ui_helpers
import screens
import models
import utils
from kivy.utils import platform
from kivymd.toast import toast
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp


class DominoApp(MDApp):

    def build(self):        
        self.players = {}  # {player.name : Player}
        self.games = {}  # {game.id : GameScore}
        self.current_game = None
        
        self.data_dir = self.user_data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        
        self.theme_cls.theme_style = "Dark"

        self._register_fonts()

        sm = ScreenManager()
        for cls, name in screens.ALL_SCREENS:
            sm.add_widget(cls(name=name))
        return sm


    def on_start(self):
        self.request_permissions()
        
        loaded_players = utils.load_players(self.data_dir)
        loaded_games = utils.load_games(self.data_dir)
    
        if loaded_players:
            self.players = loaded_players
        else:
            self.players = {}
    
        if loaded_games:
            self.games = loaded_games
        else:
            self.games = {}


    def request_permissions(self):
        # 1. Check & Request Storage Permissions (Android 11+)
        if platform == "android":
            from jnius import autoclass
            from android.permissions import request_permissions, Permission
            
            # Standard permissions (good to have)
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE
            ])

            # Check for "All Files Access" (Android 11/API 30+)
            Environment = autoclass("android.os.Environment")
            if not Environment.isExternalStorageManager():
                print("Requesting All Files Access...")
                
                # Create an Intent to open the specific settings page
                Intent = autoclass("android.content.Intent")
                Settings = autoclass("android.provider.Settings")
                Uri = autoclass("android.net.Uri")
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                # Open: Settings > Apps > Special App Access > All Files Access > [Your App]
                try:
                    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
                    uri = Uri.parse("package:" + PythonActivity.mActivity.getPackageName())
                    intent.setData(uri)
                    PythonActivity.mActivity.startActivity(intent)
                    toast("Please allow 'All Files Access' to save data.")
                except Exception as e:
                    print(f"Error requesting permission: {e}")
                    toast("Could not open settings for file permission.")

     


    def _register_fonts(self):
        font_path = os.path.join(os.path.dirname(__file__), "data", "breakaway.ttf")
        if os.path.exists(font_path):
            try:
                LabelBase.register(
                    name="BreakAway",
                    fn_regular=font_path,
                )
            except Exception:
                print("Font registration failed")
    

    def start_game(self, names):
        self.current_game = models.GameScore(names)
        self.root.current = "game"


    def end_game(self):
        print("DominoApp -> end_game()")
        game = self.current_game
        if not game or not game.finished:
            print("App: not game or not game.finished")
            return
        self.games[game.id] = game    # Add game to self.games
        for name, score in game.totals.items():
            p = self.players.get(name)
            if score > self.players[name].highest_score:
                self.players[name].highest_score = score
            if game.winner == name:
                self.players[name].wins += 1
            else:
                self.players[name].losses += 1
        utils.save_players(self.players, self.app_path)
        utils.save_games(self.games, self.app_path)
            

    def add_player(self, name):
        if not name:
            return
        if name in self.players.keys():
            print(f"{name} already exists")
            return
        else:
            self.players[name] = models.Player(name)
            utils.save_players(self.players, self.app_path)


    def delete_player(self, name):
        if not name:
            return

        def _do_delete():
            self.players.pop(name, None)
            utils.save_players(self.players, self.app_path)
            self.del_confirm.dismiss()

        self.del_confirm = ui_helpers.ConfirmDialog(
            title="Delete Player?",
            text=f"Do you want to delete {name}?",
            on_confirm = _do_delete 
        )
        self.del_confirm.open()


    def add_game(self, game):
        if not game or not game.id:
            return
    
        self.games[game.id] = game
        self.recompute_player_stats()
        utils.save_games(self.games, self.data_dir)
        utils.save_players(self.players, self.data_dir)
    
    
    def delete_game(self, game):
        if not game or not game.id:
            return
    
        def _do_delete():
            if game.id not in self.games:
                print(f"delete_game: game {game.id} not found")
                return
            del self.games[game.id]
            print(f"Removed game {game.id}")
            self.recompute_player_stats()
            utils.save_games(self.games, self.data_dir)
            utils.save_players(self.players, self.data_dir)
        self.del_game_conf = ui_helpers.ConfirmDialog(
            title="Delete Game?",
            text="Are you sure you want to permanently delete this game?",
            on_confirm=_do_delete
        )
        self.del_game_conf.open()
    
    
    def recompute_player_stats(self):
        for p in self.players.values():
            p.wins = 0
            p.losses = 0
            p.highest_score = 0
    
        for game in self.games.values():
            if not game.finished or not game.winner:
                continue
    
            for name, score in game.totals.items():
                player = self.players.get(name)
                if not player:
                    continue
    
                if score > player.highest_score:
                    player.highest_score = score
    
                if name == game.winner:
                    player.wins += 1
                else:
                    player.losses += 1


    def go_back(self):
        self.root.current = "menu"
    
    
    def import_data(self, date):
        self.players, self.games = utils.import_data(date)
       # players = {k:models.Player.from_dict(p) for k,p in data['players'].items()}
#        games = {id:models.GameScore.from_dict(g) for id,g in data['games'].items()}
#        self.players = players
#        self.games = games
        print("Data imported!")
        utils.save_games(self.games, self.data_dir)
        utils.save_players(self.players, self.data_dir)
        self.root.current = "menu"


    @property
    def app_path(self):
        return self.data_dir
