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
        self.players = []
        self.games = []
        self.current_game = None

        self.theme_cls.theme_style = "Dark"
        self._register_fonts()

        sm = ScreenManager()
        for cls, name in ALL_SCREENS:
            sm.add_widget(cls(name=name))
        return sm

    def on_start(self):
        #if platform == "android" and 1 == 2:
#            from android.permissions import request_permissions, Permission

#            request_permissions(
#                [Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE],
#                self._on_permissions_result
#            )
#        else:
        if 1 == 1:
            self._load_data()

    def _on_permissions_result(self, permissions, results):
        if all(results):
            self._load_data()
        else:
            toast("Storage permission denied")

    def _load_data(self):
        self.players = load_players() or []
        self.games = load_games() or []
        print(f"{len(self.players)} players loaded")
        print(f"{len(self.games)} games loaded")
    
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

    def save_players(self, name=None):
        if not self.players:
            self.players = []
    
        if name and isinstance(name, str):
            if not any(p.name == name for p in self.players):
                self.players.append(Player(name))
        save_players(self.players)
        print("Players saved")
    

    def save_games(self, game = None):
        if self.games is None:
            self.games = []
        if game != None and isinstance(game, GameScore):
            newgame = True
            for i,g in enumerate(self.games):
                if g.id == game.id:
                    self.games[i] = g
                    newgame = False
                    break
            if newgame:
                self.games.append(game)
                print(f"{game.to_dict()}\n")
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
        self.root.current = "game"
    
    def end_game(self):
        game = self.current_game
        if not game or not game.finished:
            return
        for name, score in game.totals.items():
            for player in self.players:
                if player.name == name:
                    player.set_highest_score(score)
                    break
        self.save_games(game)
        self.save_players()
        self.current_game = None
        self.refresh_players()

    
    # ======================================================
    # PLAYER FUNCTIONS
    # ======================================================

    def compute_player_stats(self):
        stats = {}
        for g in self.games:
            if not g.finished or not g.winner:
                continue
            for name in g.totals:
                stats.setdefault(name, {"wins": 0, "losses": 0})
            stats[g.winner]["wins"] += 1    #Add to wins
            for name in g.totals:
                if name != g.winner:
                    stats[name]["losses"] += 1    #Add to losses
        return stats


    def sync_players_from_games(self):
        stats = self.compute_player_stats()
        for p in self.players:
            if p.name in stats:
                p.wins = stats[p.name]["wins"]
                p.losses = stats[p.name]["losses"]
            else:
                p.wins = 0
                p.losses = 0       
        self.save_players()
        print("Players synced")

    def recompute_high_scores(self):
        for p in self.players:
            p.highest_score = 0
    
        for g in self.games:
            if not g.finished:
                continue
            for name, score in g.totals.items():
                for p in self.players:
                    if p.name == name:
                        p.set_highest_score(score)

    def refresh_players(self):
        self.players = load_players()
        self.sync_players_from_games()
        return self.players
    
    def reset_players(self, player = None):
        if isinstance(player, Player) and any(p.name == player.name for p in self.players):
            player.reset_stats()
            print(f"{player.name} has been reset")
        if player is None:
            for p in self.players:
                p.reset_stats()
                print(f"{p.name} has been reset")
        self.save_players()
    
    
    def delete_player(self, player):
        # Ensure we have the name string to compare
        target_name = player.name if isinstance(player, Player) else player     
        # Find the player object in the list that matches the name
        player_to_remove = None
        for p in self.players:
            if p.name == target_name:
                player_to_remove = p
                break       
        # Remove the object from the list
        if player_to_remove:
            self.players.remove(player_to_remove)
            print(f"Player {player_to_remove.name} deleted.")


    # ======================================================
    # GAME HISTORY FUNCTIONS
    # ======================================================

    def delete_game(self, x_game):
        if not x_game or not isinstance(x_game, GameScore):
            print("APP: Invalid game to delete.")
            return
        try:
            self.games.remove(x_game)
            self.save_games()
        except Exception as e:
            print(f"ERROR IN DominoApp.delete_game:\n{str(e)}")
            return