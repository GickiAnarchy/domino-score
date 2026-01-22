from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen


class CreatePlayerScreen(MDScreen):

    def save(self):
        name = self.ids.player_name.text.strip()
        if not name:
            print("Invalid name in create_player")
            return
        self.app.add_player(name)
        self.ids.player_name.text = ""
        self.manager.current = "menu"

    @property
    def app(self):
        return MDApp.get_running_app()
