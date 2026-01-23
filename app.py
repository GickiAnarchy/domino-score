import os
import logging
import ui_helpers
import screens
import models
import utils

#from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp


class DominoApp(MDApp):

    def build(self):
        self.players = {}  # {player.name : Player}
        self.games = {}  # {game.id : GameScore}

        self.current_game = None

        sm = ScreenManager()
        for cls, name in screens.ALL_SCREENS:
            sm.add_widget(cls(name=name))
        return sm


    def on_start(self):
        self.players = utils.load_players(self.app_path)
        self.games = utils.load_games(self.app_path)


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
        game = self.current_game
        if not game or not game.finished:
            return
        for name, score in game.totals.items():
            p = self.players.get(name)
            if score > p.highest_score:
                self.players[name].highestscore = score
            if game.winner == name:
                self.players[name].wins += 1
            else:
                self.players[name].losses += 1
            

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
        if not game:
            return
        if game.id in self.games.keya():
            print("Game already exists in Games History")
            return
        self.games[game.id] = game
        utils.save_games(self.games, self.app_path)
        self.current_game = None
    
    
    def delete_game(self, game):
        if not game:
            return
        def _do_delete():
            self.players.pop()
            utils.save_games(self.games, self.app_path)
        
        self.del_player_conf = ui_helpers.ConfirmDialog(
        title="Delete Player?",
        text="Are you sure you want to permanently delete this game??", 
        on_confirm=_do_delete)
        
        self.del_player_conf.open()
    
    
    @property
    def app_path(self):
        return self.user_data_dir
