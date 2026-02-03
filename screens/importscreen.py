from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem

import utils


class ImportScreen(MDScreen):


    def import_data(self, data):
        self.app.import_data(data)


    @property
    def app(self):
        return MDApp.get_running_app()