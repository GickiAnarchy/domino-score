import os
import logging
import random

from screens import ALL_SCREENS
from models import Player, GameScore
from utils import (
    setup_logger,
    get_export_dir,
    load_players,
    save_players,
    load_games,
    save_games,
)

from constants import COLORS

from kivy.core.text import LabelBase
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivymd.toast import toast


class DominoApp(MDApp):

    # ======================================================
    # APP BOOT
    # ======================================================

    def build(self):
        setup_logger()

        self.data_dir = get_export_dir()
        self.players_file = os.path.join(self.data_dir, "players.dom")
        self.games_file = os.path.join(self.data_dir, "games.dom")

        self.players = load_players(self.players_file)
        self.games = load_games(self.games_file)

        self.current_game = None

        self.sync_players_from_games()

        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"

        self._register_fonts()

        sm = ScreenManager()
        for cls, name in ALL_SCREENS:
            sm.add_widget(cls(name=name))

        toast("version 0.9.4")
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

    def save_players(self):
        save_players(self.players_file, self.players)

    def save_games(self):
        save_games(self.games_file, self.games)

    # ======================================================
    # GAME FLOW
    # ======================================================

    def start_game(self, names):
        if not names or len(names) < 2:
            return
        valid_names = [name for name in names if name in self.players]
        if len(valid_names) < 2:
            logging.warning("Not enough valid players")
            return
        self.current_game = GameScore(valid_names)
        self.root.current = "game"
    
    def end_current_game(self):
        game = self.current_game
        if not game:
            return
        if not game.totals:
            toast("No scores yet")
            return
        game.finish()
        if game.winner:
            toast(f"{game.winner} wins!")
            self.games.append(game)
            self.save_games()
            self.sync_players_from_games()
        else:
            toast("Tie at the top — another hand!")
            game.finished = False
            return  # stay in game screen
        self.current_game = None
        self.root.current = "menu"
        
    # ======================================================
    # EDITED GAME SAVE
    # ======================================================

    def save_edited_game(self, edited_game):
        replaced = False
        for i, g in enumerate(self.games):
            if g.id == edited_game.id:
                self.games[i] = edited_game
                replaced = True
                break
        if not replaced:
            self.games.append(edited_game)
        self.save_games()
        self.sync_players_from_games()
        self.current_game = None
        self.root.current = "history"

    # ======================================================
    # STATS
    # ======================================================

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

    # ======================================================
    # UTIL
    # ======================================================

    def refresh_players(self):
        self.players = load_players(self.players_file)
        self.sync_players_from_games()
        return self.players