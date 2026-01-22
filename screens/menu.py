from kivymd.uix.screen import MDScreen
import constants
import random


class MenuScreen(MDScreen):
    def get_fact(self):
        return random.choice(constants.FACTS)
