from kivymd.uix.screen import MDScreen
from kivymd.uix.menu.menu import MDDropdownMenu
from kivymd.app import MDApp


class StatsScreen(MDScreen):
    def on_enter(self):
        app = MDApp.get_running_app()
         
        
        self.stats_list = self.ids.stats_list
        self.player_selection = MDDropboxMenu()