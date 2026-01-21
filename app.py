import os
import logging
import random
from screens import ALL_SCREENS
from models import Player, GameScore
from utils import save_games, load_games, save_players, load_players
from constants import COLORS
from kivy.utils import platform
from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.toast import toast
from kivy.clock import Clock


class DominoApp(MDApp):

    def build(self):
        self.players = {}   # {player.name : Player}
        self.games = {}     # {game.id : GameScore}

        self.current_game = None

        sm = ScreenManager()
        for cls, name in ALL_SCREENS:
            sm.add_widget(cls(name=name))
        return sm


    def on_start(self):
        self.players = load_players()
        self.games = load_games()


    def _register_fonts(self):
        font_path = os.path.join(
            os.path.dirname(__file__), "data", "breakaway.ttf")
        if os.path.exists(font_path):
            try:
                LabelBase.register(
                    name="BreakAway",
                    fn_regular=font_path,)
            except Exception:
                logging.exception("Font registration failed")


    def start_game(self, names):
        pass

    
    def end_game(self):
        pass
