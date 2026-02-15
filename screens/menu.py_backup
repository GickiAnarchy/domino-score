from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
import constants
import random


class MenuScreen(MDScreen):
    def on_enter(self):
        self.ids.title_label.font_name = "BreakAway"
    
    def get_fact(self):
        return random.choice(constants.FACTS)
