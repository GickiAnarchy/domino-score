from kivymd.uix.screen import MDScreen
from constants import FACTS
import random


class MenuScreen(MDScreen):
    def get_fact(self):
        return random.choice(FACTS)