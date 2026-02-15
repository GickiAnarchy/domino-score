from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivy.clock import Clock
from kivy.metrics import dp
from domino_widgets import DominoTileWidget
import models


class BoardScreen(MDScreen):
    
    def on_enter(self, *args):
        self.hand_tiles = []
        self.board_tiles = []
        self._setup_new_game()
        Clock.schedule_once(self.refresh_ui, 0)

    def _setup_new_game(self):
        all_tiles = models.DominoTile.create_double_sixes()
        random_deck = list(all_tiles)
        import random
        random.shuffle(random_deck)
        self.hand_tiles = random_deck[:7]
        self.board_tiles = []

    def refresh_ui(self, *args):
        self._refresh_hand()
        self._refresh_board()

    def _refresh_hand(self):
        hand = self.ids.hand_area
        hand.clear_widgets()
        tw, th = self.tile_size()

        for model in self.hand_tiles:
            tile = DominoTileWidget(
                value_top=model.value_top,
                value_bottom=model.value_bottom,
                size=(tw, th)
            )
            tile.model = model
            # Disable scatter behavior for tiles in hand
            tile.do_translation_x = False
            tile.do_translation_y = False
            tile.do_scale = False
            hand.add_widget(tile)

    def _refresh_board(self):
        board = self.ids.board_area
        board.clear_widgets()
        x, y = dp(40), dp(40)
        tw, th = self.tile_size()

        for model in self.board_tiles:
            tile = DominoTileWidget(
                value_top=model.value_top,
                value_bottom=model.value_bottom,
                size=(tw, th)
            )
            tile.model = model
            tile.pos = (x, y)
            # Enable scatter behavior for tiles on board
            tile.do_translation_x = True
            tile.do_translation_y = True
            board.add_widget(tile)

            x += tw + dp(15)
            if x > self.width - tw:
                x = dp(40)
                y += th + dp(15)

    def play_tile(self, model):
        if model in self.hand_tiles:
            self.hand_tiles.remove(model)
            self.board_tiles.append(model)
            self.refresh_ui()

    def tile_size(self):
        hand = self.ids.hand_area
        if not hand.width:
            return dp(40), dp(80)
        
        spacing = hand.spacing if isinstance(hand.spacing, (int, float)) else hand.spacing[0]
        padding = hand.padding[0] + hand.padding[2]
        
        available_width = hand.width - (spacing * 6) - padding
        w = available_width / 7
        h = w * 2
        return w, h


    @property
    def app(self):
        return MDApp.get_running_app()
