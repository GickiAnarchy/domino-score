import json
import logging
import os
from datetime import datetime
from uuid import uuid4
from kivy.utils import platform
from models import Player, GameScore



def get_export_dir():
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


PLAYERS_FILE  = os.path.join(get_export_dir(), "players.dom")
GAMES_FILE  = os.path.join(get_export_dir(), "games.dom")

###
#   PLAYERS
###

def save_players(players):
    if not players:
        print("utils.save_players(players) -> players is not valid")
        return
    data = {n: p.to_dict() for n,p in players.items()}
    with open(PLAYERS_FILE, "w") as f:
        json.dump(data, f, indent = 2)
    print("Players have been saved")
    return
    

def load_players() -> dict:
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




###
#   GAMES
###

def save_games(games):
    if not games:
        print("utils.save_games(games) -> games is not valid")
        return
    data = {n: g.to_dict() for n,g in games.items()}
    with open(GAMES_FILE, "w") as f:
        json.dump(data, f, indent = 2)
    print("Games have been saved")
    return


def load_games() -> dict:
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
    print("Ganes have been loaded")
    return data

