from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.metrics import dp
from domino_widgets import DominoTileWidget
import models


class BoardScreen(MDScreen):

    @property
    def app(self):
        return MDApp.get_running_app()
