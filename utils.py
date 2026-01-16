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



def save_players(path, players: dict):
    """
    players: dict[str, Player]
    """
    data = [p.to_dict() for p in players.values()]
    atomic_write_json(path, data)


def load_players(path):
    raw = safe_load_json(path, [])
    players = {}

    for item in raw:
        try:
            p = Player.from_dict(item)
            if p.name:
                players[p.name] = p
        except Exception:
            logging.exception("Failed to load player")

    return players
    
    
def save_games(path, games):
    """
    games: list[GameScore]
    """
    data = [g.to_dict() for g in games]
    atomic_write_json(path, data)


def load_games(path):
    raw = safe_load_json(path, [])
    games = []

    for item in raw:
        try:
            games.append(GameScore.from_dict(item))
        except Exception:
            logging.exception("Failed to load game")

    return games


