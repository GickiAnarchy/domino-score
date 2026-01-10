from kivy.utils import get_color_from_hex



DATA_DIR = None
SAVE_FILE = None
GAMES_FILE = None

MAX_POINTS = 300
SELECTED_COLOR = get_color_from_hex("#4CAF50")
DEFAULT_COLOR = get_color_from_hex("#1E88E5")

FACTS = [
    "All Hail King Dingle!!",
    "Can you count to five?",
    "Draw ya plenty of 'em.",
    "Is it ridiculous yet?",
    "The opponent can't make any points\noff the 2-3 domino.",
    "Careful holding on\nto that Double-Six",
    "Just a nickel at a time.",
    "Eight, skate, and donate.",
    "Niner, Not a tight vaginer",
    "Ready for a spanking?",
    "Too many doubles in your hand?\nYou might be able to call for\na redraw!",
    "Whoever leads the hand\nchooses how many dominoes \nto start with."
]

COLORS = [
    "Red", "Pink", "Purple", "DeepPurple", "Indigo", "Blue",
    "LightBlue", "Cyan", "Teal", "Green", "LightGreen", "Lime",
    "Yellow", "Amber", "Orange", "DeepOrange", "Brown", "Gray", "BlueGray"]

THEME_BLK_RED = ["Black", "Red", "Gray"]