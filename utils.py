import json
import logging
import os
import random
from datetime import datetime
from uuid import uuid4

from kivy.utils import platform



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
        format="%(asctime)s | %(levelname)s | %(message)s",)
    logging.info("=== App starting ===")

def ids_ready(screen, *names):
    return all(name in screen.ids for name in names)

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

def request_storage_permissions():
    if platform != "android":
        return

    try:
        from android.permissions import request_permissions, Permission
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
        ])
    except Exception as e:
        logging.warning(f"Permission request skipped: {e}")

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