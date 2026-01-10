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
    tmp_path = f"{path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)  # atomic on Android/Linux
    except Exception:
        logging.exception(f"Failed atomic write: {path}")
        try:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass

def get_data_dir():
    if platform == "android":
        from android.storage import app_storage_path
        return app_storage_path()
    return os.getcwd()


def get_export_dir():
    if platform == "android":
        try:
            from android.storage import primary_external_storage_path, app_storage_path
            base = primary_external_storage_path()
        except Exception:
            # Fallback to internal app storage (always safe)
            from android.storage import app_storage_path
            base = app_storage_path()
        path = os.path.join(base, "Download", "DominoScorebook")
    else:
        path = os.path.join(os.getcwd(), "exports")
    try:
        os.makedirs(path, exist_ok=True)
    except Exception:
        path = os.getcwd()
    return path



class DominoApp(MDApp):
    def save_players(self):
        data = {
            "version": 1,
            "players": {
                name: {
                    "wins": player.wins,
                    "losses": player.losses,}
                for name, player in self.players.items()}}
        atomic_write_json(SAVE_FILE, data)
        
    def load_players(self):
        if not os.path.exists(SAVE_FILE):
            return {}    
        # Empty file guard
        if os.path.getsize(SAVE_FILE) == 0:
            logging.warning("Players save file is empty")
            return {}    
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
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
        games = safe_load_json(GAMES_FILE, [])
    
        # Replace game with same date
        replaced = False
        for i, g in enumerate(games):
            if g.get("date") == edited_game.date:
                games[i] = edited_game.to_dict()
                replaced = True
                break
    
        # Fallback: append if not found
        if not replaced:
            games.append(edited_game.to_dict())
    
        atomic_write_json(GAMES_FILE, games)
    
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