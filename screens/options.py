from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast

import utils


class OptionsScreen(MDScreen):
    
    def export_data(self):
        path = utils.export_to_shared(
            self.app.players,
            self.app.games
        )
        toast(f"Exported to {path}")


    def import_data(self):
        try:
            self.app.players, self.app.games = utils.import_from_shared()
            utils.save_players(self.app.players)
            utils.save_games(self.app.games)
            self.app.recompute_player_stats()
            toast("Import successful")
        except Exception as e:
            toast(str(e))


    @property
    def app(self):
        return MDApp.get_running_app()