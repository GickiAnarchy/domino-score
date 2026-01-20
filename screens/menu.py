from kivymd.uix.screen import MDScreen
from ui_helpers import MDSeparator
from constants import FACTS
import random


class MenuScreen(MDScreen):
    def get_fact(self):
        return random.choice(FACTS)