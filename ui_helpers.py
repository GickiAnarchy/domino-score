from kivy.core.text import LabelBase
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty

from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.selectioncontrol import MDCheckbox




class HistoryCheckbox(MDCheckbox):
    game_id = None

        
class MDSeparator(MDBoxLayout):
    thickness = NumericProperty(dp(1))
    color = ListProperty([1, 1, 1, 0.2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = self.thickness
        self.md_bg_color = [1, 1, 1, 0.2]
