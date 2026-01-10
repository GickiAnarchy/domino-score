from .menu import MenuScreen
from .create_player import CreatePlayerScreen
from .player_select import PlayerSelectScreen
from .game import GameScreen
from .options import OptionsScreen
from .history import HistoryScreen
from .edit_game import EditGameScreen
from .stats import StatsScreen

ALL_SCREENS = [
    (MenuScreen, "menu"),
    (CreatePlayerScreen, "create"),
    (PlayerSelectScreen, "select"),
    (GameScreen, "game"),
    (OptionsScreen, "options"),
    (HistoryScreen, "history"),
    (EditGameScreen, "edit"),
    (StatsScreen, "stats"),
]

__all__ = [
    "MenuScreen",
    "CreatePlayerScreen",
    "PlayerSelectScreen",
    "GameScreen",
    "OptionsScreen",
    "HistoryScreen",
    "EditGameScreen",
    "StatsScreen",
    "ALL_SCREENS",
]