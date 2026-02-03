from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem

import utils


class ImportScreen(MDScreen):


    def import_data(self, data):
        if ["players","games"] in data.keys():
            self.app.import_data(data)
        else:
            print("Import is wrong format")
            self.root.current = "menu"


    @property
    def app(self):
        return MDApp.get_running_app()