import os
import logging
import json
import random

from screens import ALL_SCREENS
from models import Player, GameScore
from utils import setup_logger, get_data_dir, get_export_dir, atomic_write_json, safe_load_json 
from constants import MAX_POINTS, COLORS

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



class DominoApp(MDApp):
    def build(self):
        setup_logger()
        self.data_dir = get_data_dir()
        os.makedirs(self.data_dir, exist_ok=True)
        self.save_file = os.path.join(self.data_dir, "players.dom")
        self.games_file = os.path.join(self.data_dir, "games.dom")
        self.players = self.load_players()
        self.sync_players_from_games()
        self.current_game = None
        self.theme_cls.primary_palette = random.choice(COLORS)
        self.theme_cls.theme_style = "Dark"
        font_path = os.path.join(os.path.dirname(__file__), "data", "breakaway.ttf")
        if os.path.exists(font_path):
            try:
                LabelBase.register(
                    name="BreakAway",
                    fn_regular=font_path
                )
            except Exception:
                logging.exception("Failed to register BreakAway font")
        else:
            logging.warning("BreakAway font not found, using default")
        sm = ScreenManager()
        for cls, name in ALL_SCREENS:
            sm.add_widget(cls(name=name))

        toast("version 0.9.4")
        return sm
        
    def save_players(self):
        data = {
            "version": 1,
            "players": {
                name: {
                    "wins": player.wins,
                    "losses": player.losses,}
                for name, player in self.players.items()}}
        atomic_write_json(self.save_file, data)
        
    def load_players(self):
        if not os.path.exists(self.save_file):
            return {}    
        # Empty file guard
        if os.path.getsize(self.save_file) == 0:
            logging.warning("Players save file is empty")
            return {}    
        try:
            with open(self.save_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            logging.error("Players save file contains invalid JSON")
            return {}
        except Exception:
            logging.exception("Unexpected error loading players")
            return {}    
        players_data = data.get("players")
        if not isinstance(players_data, dict):
            logging.error("Players save file has invalid schema")
            return {}    
        players = {}
        for name, stats in players_data.items():
            try:
                players[name] = Player(
                    name=name,
                    wins=int(stats.get("wins", 0)),
                    losses=int(stats.get("losses", 0)),)
            except Exception:
                logging.warning(f"Skipping invalid player entry: {name}")    
        return players

    def save_edited_game(self, edited_game):
        games = safe_load_json(self.games_file, [])    
        # Replace game with same date
        replaced = False
        for i, g in enumerate(games):
            if g.get("id") == edited_game.id:
                games[i] = edited_game.to_dict()
                replaced = True
                break    
        # Fallback: append if not found
        if not replaced:
            games.append(edited_game.to_dict())    
        atomic_write_json(self.games_file, games)    
        self.current_game = None
        self.root.current = "history"    
            
    def start_game(self, names):
        if not names or len(names) < 2:
            return    
        players = []
        for name in names:
            player = self.players.get(name)
            if player:
                players.append(player)    
        if len(players) < 2:
            logging.warning("Not enough valid players to start game")
            return    
        self.current_game = GameScore(players)        
        self.root.current = "game"

    def finish_game(self):
        game = self.current_game
        if not game:
            return    
        games1 = safe_load_json(self.games_file, [])
        games = [g for g in games1 if g.get("id") != game.id]
        games.append(game.to_dict())
        atomic_write_json(self.games_file, games)   
        self.current_game = None
        self.root.current = "menu"

    def compute_player_stats(self):
        stats = {}
        games = safe_load_json(self.games_file, [])    
        for g in games:
            if not g.get("finished"):
                continue    
            winner = g.get("winner")
            if not winner:
                continue  
            for name in g.get("totals", {}):
                stats.setdefault(name, {"wins": 0, "losses": 0})   
            stats[winner]["wins"] += 1
            for name in g["totals"]:
                if name != winner:
                    stats[name]["losses"] += 1    
        return stats

    def sync_players_from_games(self):
        computed = self.compute_player_stats()
        for name, player in self.players.items():
            if name in computed:
                player.wins = computed[name]["wins"]
                player.losses = computed[name]["losses"]
            else:
                player.wins = 0
                player.losses = 0


