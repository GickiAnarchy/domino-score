import os
import logging
from ui_helpers import ConfirmDialog
from screens import ALL_SCREENS
from models import Player, GameScore
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
        for cls, name in ALL_SCREENS:
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
                logging.exception("Font registration failed")

    def start_game(self, names):
        pass

    def end_game(self):
        pass

    def add_player(self, name):
        if not name:
            return
        if name in self.players.keys():
            print(f"{name} already exists")
            return
        else:
            self.players[name] = Player(name)
            utils.save_players(self.players, self.app_path)

    def delete_player(self, name):
        if not name:
            return

        def _do_delete():
            self.players.pop(name, None)
            utils.save_players(self.players, self.app_path)

        del_confirm = ConfirmDialog(
            title="Delete Player?",
            text=f"Do you want to delete {name}?",
            on_confirm=_do_delete,
        )
        del_confirm.open()
    
    
    @property
    def app_path(self):
        return self.user_data_dir
