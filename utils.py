import json
import logging
import os
from datetime import datetime
from uuid import uuid4

from kivy.utils import platform

from models import Player, GameScore


# ==========================================================
# LOGGING
# ==========================================================

def setup_logger():
    try:
        if platform == "android":
            from android.storage import app_storage_path
            base = app_storage_path()
        else:
            base = os.getcwd()

        log_dir = os.path.join(base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, "domino.log")
    except Exception:
        log_file = "domino.log"

    logging.basicConfig(
        filename=log_file,
        filemode="a",
        level=logging.DEBUG,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    logging.info("=== App starting ===")


# ==========================================================
# GENERAL HELPERS
# ==========================================================

def ids_ready(screen, *names):
    """Return True if all ids exist on the screen"""
    return all(name in screen.ids for name in names)


# ==========================================================
# FILE SYSTEM
# ==========================================================

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



# ==========================================================
# JSON SAFE IO
# ==========================================================

def safe_load_json(path, default):
    if not path or not os.path.exists(path):
        return default

    try:
        if os.path.getsize(path) == 0:
            return default
    except Exception:
        return default

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, type(default)) else default
    except Exception:
        logging.exception(f"Failed to load JSON: {path}")
        return default


def atomic_write_json(path, data):
    tmp = f"{path}.tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    except Exception:
        logging.exception(f"Atomic write failed: {path}")
        try:
            if os.path.exists(tmp):
                os.remove(tmp)
        except Exception:
            pass


# ==========================================================
# PLAYERS
# ==========================================================

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


# ==========================================================
# GAMES
# ==========================================================

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