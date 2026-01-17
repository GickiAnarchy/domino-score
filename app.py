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

    # ======================================================
    # APP BOOT
    # ======================================================

    def build(self):        
        self.current_game = None
        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"
        self._register_fonts()
        
        self.players = load_players()
        self.games = load_games()
        
        self.current_game = None
        
        sm = ScreenManager()
        for cls, name in ALL_SCREENS:
            sm.add_widget(cls(name=name))
        return sm
    
    # ======================================================
    # FONTS
    # ======================================================

    def _register_fonts(self):
        font_path = os.path.join(
            os.path.dirname(__file__), "data", "breakaway.ttf"
        )
        if os.path.exists(font_path):
            try:
                LabelBase.register(
                    name="BreakAway",
                    fn_regular=font_path,
                )
            except Exception:
                logging.exception("Font registration failed")

    # ======================================================
    # SAVE / LOAD
    # ======================================================

    def save_players(self, player = None):
        if player != None and isinstance(player, Player):
            newplayer = True
            for i,p in enumerate(self.players):
                if player.name == p.name:
                    self.players[i] = player
                    newplayer = False
                    break
            if newplayer:
                self.players.append(player)
                print("New player added")
        save_players(self.players)
        print("Players saved")

    def save_games(self, game = None):
        if game != None and isinstance(game, GameScore):
            newgame = True
            for i,g in enumerate(self.games):
                if g.id == game.id:
                    self.games[i] = g
                    newgame = False
                    break
            if newgame:
                self.games.append(game)
                print("New game added")
        save_games(self.games)
        print("Games saved")

    # ======================================================
    # GAME FLOW
    # ======================================================


    def start_game(self, names):
        if not names or len(names) < 2:
            print("Need at least two players to start game.")
            return
        self.current_game = GameScore(names)
        #go to game screen
        #self.root.current = "game"
    
    def end_game(self):
        game = self.current_game
        if not game.finished:
            print("Game isn't finished, cannot end current game.")
            return
        self.save_games(game)
        self.current_game = None
        self.sync_players_from_games()
        self.save_players()


#
#
#
    def compute_player_stats(self):
        stats = {}
        for g in self.games:
            if not g.finished or not g.winner:
                continue
            for name in g.totals:
                stats.setdefault(name, {"wins": 0, "losses": 0})
            stats[g.winner]["wins"] += 1
            for name in g.totals:
                if name != g.winner:
                    stats[name]["losses"] += 1
        return stats


    def sync_players_from_games(self):
        stats = self.compute_player_stats()
        for p in self.players.values():
            if p.name in stats:
                p.wins = stats[p.name]["wins"]
                p.losses = stats[p.name]["losses"]
            else:
                p.wins = 0
                p.losses = 0
        self.save_players()
        print("Players synced")


    def refresh_players(self):
        self.players = load_players()
        self.sync_players_from_games()
        return self.players