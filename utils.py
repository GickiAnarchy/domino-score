import json
import logging
import os
from datetime import datetime
from uuid import uuid4

from kivy.utils import platform

from models import Player, GameScore



#=================================================
# FILE SYSTEM
# ================================================

def get_data_dir():
    if platform == "android":
        from android.storage import app_storage_path
        return app_storage_path()
    return os.getcwd()


def get_export_dir():
    """
    Shared export folder (Android Downloads / Desktop exports)
    """
    if platform == "android":
        try:
            # This is the modern way to get the Downloads folder on Android
            from android.storage import primary_external_storage_path
            primary_storage = primary_external_storage_path()
            path = os.path.join(primary_storage, "Download", "DominoScorebook")
        except Exception as e:
            logging.error(f"Failed to get primary storage: {e}")
            from android.storage import app_storage_path
            path = app_storage_path()
    else:
        path = os.path.join(os.getcwd(), "exports")

    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create directory {path}: {e}")
            return os.getcwd()

    return path


##
#    FILE I/O
##
    
def save_players(players):
    """
    players: list[Player]
    """
    path = os.path.join(get_export_dir(), "players.dom")
    if not isinstance(players, list):
        print("Players need to be in a list")
        return
    data = [p.to_dict() for p in players]
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent = 2)
    except Exception as e:
        print(e)
        return
    print("Players saved")
    

def load_players():    
    players = []
    path = os.path.join(get_export_dir(), "players.dom")
    if os.path.exists(path):
        try:
            with open(path,"r") as f:
                players = json.load(f)
        except Exception as e:
            print(e)
            return
    return players
    
    
def save_games(games):
    """
    games: list[GameScore]
    """
    path = os.path.join(get_export_dir(), "games.dom")
    if not isinstance(games, list):
        print("Games need to be a list.")
        return
    data = [g.to_dict() for g in games]
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent = 2)
    except Exception as e:
        print(e)
        return
    print("Games saved")       


def load_games():
    raw = None
    games = []
    path = os.path.join(get_export_dir(), "games.dom")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                raw = json.load(f)
        except Exception as e:
            print(e)
            return
        for g in raw:
            try:
                games.append(GameScore.from_dict(g))
            except Exception as e:
                print(e)
                return
    else:
        print("No saved games file")p
        return
    return games


