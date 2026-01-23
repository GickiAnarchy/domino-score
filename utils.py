import json
import os
from kivy.utils import platform
import models



def get_export_dir() -> str:    
    if platform == "android":
        try:
            from android.storage import app_storage_path
            path = app_storage_path()
        except Exception as e:
            print("Storage fallback:", e)
            #path = "/data/data/com.gicki.dominoscores/files"
            path = "."
    else:
        path = os.path.join(os.getcwd(), "exports")
    os.makedirs(path, exist_ok=True)
    return path



###
#   PLAYERS
###


def save_players(players = None, f_path = None):
    if players == None or not f_path:
        return
    p_file = os.path.join(get_export_dir(), "players.json")
    data = {n: p.to_dict() for n,p in players.items()}
    try:
        with open(p_file, "w") as f:
            json.dump(data, f, indent = 2)
    except Exception as e:
        print(f"UTILS ERROR: {e}")
        return
    print("Players have been saved")
    return
    

def load_players(f_path) -> dict:
    if not f_path:
        return
    p_file = os.path.join(f_path,"players.json")
    if not os.path.exists(p_file):
        return {}
    try:
        with open(p_file, "r") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"utils.load_players -> {e}")
        return {}
    try:
        data = {n: models.Player.from_dict(p) for n,p in raw.items()}

    # FOR DEBIGGING:
        print(data.keys())

    except Exception as e:
        print(f"utils.load_players -> {e}")
        return {}
    print("Players have been loaded")
    return data


###
#   GAMES
###


def save_games(games = None, f_path = None):
    if not games or not f_path:
        print("utils.save_games(games) -> games is not valid")
        return
    g_file = os.path.join(f_path, "games.json")
    data = {n: g.to_dict() for n,g in games.items()}
    try:
        with open(g_file, "w") as f:
            json.dump(data, f, indent = 2)
    except Exception as e:
        print(f"UTILS ERROR: {e}")
        return
    print("Games have been saved")
    return


def load_games(f_path) -> dict:
    if not f_path:
        return
    g_file = os.path.join(f_path, "games.json")
    if not os.path.exists(g_file):
        return {}
    try:
        with open(g_file, "r") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"utils.load_games() -> {e}")
        return {}
    try:
        data = {id: models.GameScore.from_dict(g) for id, g in raw.items()}
    except Exception as e:
        print(f"utils.load_games() -> {e}")
        return {}
    print("Games have been loaded")
    return data
