from kivymd.uix.screen import MDScreen
from kivymd.uix.menu.menu import MDDropdownMenu


class StatsScreen(MDScreen):
    def on_enter(self):
        self.stats_list = self.ids.stats_list
        