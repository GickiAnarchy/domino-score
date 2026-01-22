import json
import os
from kivy.utils import platform
from models import Player, GameScore


"""
def get_export_dir() -> str:    
    if platform == "android":
        try:
            from android.storage import app_storage_path
            path = app_storage_path()
        except Exception as e:
            print("Storage fallback:", e)
            path = "/data/data/com.gicki.dominoscores/files"
    else:
        path = os.path.join(os.getcwd(), "exports")
    os.makedirs(path, exist_ok=True)
    return path
"""


"""
def get_export_dir_wrapper() -> str:
    export_dir = None
    try:
        export_dir = get_export_dir()
    except Exception as e:
        print(f"utils.get_export_dir_wrapper() -> \n{e}")
    finally:
        return export_dir
"""


###
#   PLAYERS
###

"""
def save_players(players):
    if not players:
        print("utils.save_players(players) -> players is not valid")
        return
    PLAYERS_FILE = get_players_file()
    data = {n: p.to_dict() for n,p in players.items()}
    with open(PLAYERS_FILE, "w") as f:
        json.dump(data, f, indent = 2)
    print("Players have been saved")
    return
"""

"""
def load_players() -> dict:
    PLAYERS_FILE = get_players_file()
    if not os.path.exists(PLAYERS_FILE):
        return {}
    try:
        with open(PLAYERS_FILE, "r") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"utils.load_players -> {e}")
        return {}
    try:
        data = {n: Player.from_dict(p) for n,p in raw.items()}
    except Exception as e:
        print(f"utils.load_players -> {e}")
        return {}
    print("Players have been loaded")
    return data
"""

"""
def get_players_file() -> str:
    path = None
    ex_dir = get_export_dir_wrapper()
    try:
        path  = os.path.join(ex_dir, "players.dom")
    except Exception as e:
        print(f"utils.get_players_file() -> Error in creating path\n{e}")
    finally:
        return path
"""


###
#   GAMES
###

"""
def save_games(games):
    if not games:
        print("utils.save_games(games) -> games is not valid")
        return
    GAMES_FILE = get_games_file()
    data = {n: g.to_dict() for n,g in games.items()}
    with open(GAMES_FILE, "w") as f:
        json.dump(data, f, indent = 2)
    print("Games have been saved")
    return
"""

"""
def load_games() -> dict:
    GAMES_FILE = get_games_file()
    if not os.path.exists(GAMES_FILE):
        return {}
    try:
        with open(GAMES_FILE, "r") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"utils.load_games() -> {e}")
        return {}
    try:
        data = {id: GameScore.from_dict(g) for id, g in raw.items()}
    except Exception as e:
        print(f"utils.load_games() -> {e}")
        return {}
    print("Games have been loaded")
    return data
"""


"""
def get_games_file() -> str:
    path = None
    ex_dir = get_export_dir_wrapper()
    try:
        path  = os.path.join(ex_dir, "games.dom")
    except Exception as e:
        print(f"utils.get_games_file() -> Error in creating path\n{e}")
    finally:
        return path
"""
