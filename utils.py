import json
import os
import models
from datetime import datetime


def get_shared_folder():
    from kivy.utils import platform
    import os

    if platform == "android":
        try:
            from android.storage import primary_external_storage_path
            # This points to /storage/emulated/0/Download/DominoScorebook
            # This folder is visible to the user and survives uninstall.
            path = os.path.join(primary_external_storage_path(), "Download", "DominoScorebook")
        except Exception as e:
            print(f"Storage Error: {e}")
            path = "."
    else:
        # Desktop path
        path = os.path.join(os.getcwd(), "exports")

    # Create the folder if it doesn't exist
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        
    return path



###
#   PLAYERS
###


def save_players(players, f_path):
    if not isinstance(players, dict) or not f_path:
        raise ValueError("save_players: invalid arguments")

    p_file = os.path.join(f_path, "players.json")
    data = {n: p.to_dict() for n, p in players.items()}

    with open(p_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_players(f_path) -> dict:
    print("Loading Players.....")
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

    # FOR DEBUGGING:
        print(data.keys())

    except Exception as e:
        print(f"utils.load_players -> {e}")
        return {}
    print("Players have been loaded")
    return data


###
#   GAMES
###


def save_games(games, f_path):
    if not isinstance(games, dict) or not f_path:
        raise ValueError("save_games: invalid arguments")

    g_file = os.path.join(f_path, "games.json")
    data = {gid: g.to_dict() for gid, g in games.items()}

    with open(g_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_games(f_path) -> dict:
    print("Loading Games.....")
    if not f_path:
        return
    g_file = os.path.join(f_path, "games.json")
    if not os.path.exists(g_file):
        print("utils: g_file doesn't exist")
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




"""
Export/Import Data.
    
        {export date: {
            "Players": player data,
            "Games": gamescore data,
            }
        },
    
"""


def get_export_dates():
    exdates = [d for d in get_data().keys()]
    return exdates


def get_data():
    folder = get_shared_folder()
    file_path = os.path.join(folder, "domino_backup.json")
    if not os.path.exists(file_path):
        return {}
    with open(file_path, "r") as f:
        data = json.load(f)
    return data


def save_data(data):
    folder = get_shared_folder()
    file_path = os.path.join(folder, "domino_backup.json")
    try:
        with open(file_path, "w") as f:
            json.dump(data, f, indent = 4)
    except Exception as e:
        print(e)
        return
    print("Data exported to file")


def export_data(players: dict, games: dict):
    data = {}
    date = datetime.now()
    fdate = f"{date:%m/%d/%y %I:%M%p}"
    exdata = {
        "players": {k: p.to_dict() for k, p in players.items()},
        "games": {k: g.to_dict() for k, g in games.items()},}
    try:
        data = get_data()
    except Exception as e:
        print(e)
        return
    data[fdate] = exdata
    save_data(data)


def import_data(import_date):
    exdata = get_data()
    data = {}
    try:
        data = exdata.get(import_date)
    except Exception as e:
        print(e)
        return
    players = {k: models.Player.from_dict(v) for k, v in data["players"].items()}
    games = {k: models.GameScore.from_dict(v) for k, v in data["games"].items()}
    del exdata[import_date]
    save_data(exdata)
    return players,games