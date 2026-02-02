from .menu import MenuScreen
from .create_player import CreatePlayerScreen
from .player_select import PlayerSelectScreen
from .game import GameScreen
from .options import OptionsScreen
from .history import HistoryScreen
from .edit_game import EditGameScreen
from .stats import StatsScreen
from .editplayer import EditPlayerScreen
from .importscreen import ImportScreen

ALL_SCREENS = [
    (MenuScreen, "menu"),
    (CreatePlayerScreen, "create"),
    (PlayerSelectScreen, "select"),
    (GameScreen, "game"),
    (OptionsScreen, "options"),
    (HistoryScreen, "history"),
    (EditGameScreen, "edit"),
    (StatsScreen, "stats"),
    (EditPlayerScreen, "editplayer"),
    (ImportScreen, "import"),
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
    "EditPlayerScreen",
    "ImportScreen",
    "ALL_SCREENS",
]
