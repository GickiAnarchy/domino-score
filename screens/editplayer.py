from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen



class EditPlayerScreen(MDScreen):

    @property
    def app(self):
        return MDApp.get_running_app()
