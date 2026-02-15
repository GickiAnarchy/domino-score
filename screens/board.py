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
        # Give the screen a moment to size itself before calculating positions
        Clock.schedule_once(self.refresh_ui, 0.1)

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
        """Refresh hand with proper positioning in FloatLayout"""
        hand = self.ids.hand_area
        hand.clear_widgets()
        tw, th = self.tile_size()
        
        # Calculate total width needed for all tiles
        total_tiles = len(self.hand_tiles)
        spacing = dp(6)
        total_width = (total_tiles * tw) + ((total_tiles - 1) * spacing)
        
        # Center the tiles horizontally
        start_x = (hand.width - total_width) / 2 if hand.width > total_width else dp(8)
        y_pos = dp(8)  # Fixed y position at bottom of hand area

        for i, model in enumerate(self.hand_tiles):
            tile = DominoTileWidget(
                value_top=model.value_top,
                value_bottom=model.value_bottom,
                size=(tw, th)
            )
            tile.model = model
            
            # Disable dragging for tiles in hand
            tile.do_translation_x = False
            tile.do_translation_y = False
            tile.do_scale = False
            tile.do_rotation = False
            
            # Set position explicitly
            x_pos = start_x + (i * (tw + spacing))
            tile.pos = (x_pos, y_pos)
            
            hand.add_widget(tile)

    def _refresh_board(self):
        """Refresh board with draggable tiles"""
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
            
            # Enable dragging for tiles on board
            tile.do_translation_x = True
            tile.do_translation_y = True
            tile.do_scale = False
            tile.do_rotation = False
            
            board.add_widget(tile)

            x += tw + dp(15)
            if x > self.width - tw:
                x = dp(40)
                y += th + dp(15)

    def play_tile(self, model):
        """Move tile from hand to board"""
        if model in self.hand_tiles:
            self.hand_tiles.remove(model)
            self.board_tiles.append(model)
            # Refresh to update positions
            Clock.schedule_once(self.refresh_ui, 0.05)

    def tile_size(self):
        """Calculate appropriate tile size based on hand width"""
        hand = self.ids.hand_area
        if not hand.width or hand.width < 10:
            return dp(40), dp(80)
        
        # For FloatLayout - calculate based on available space
        padding = dp(16)  # Total left + right padding
        spacing = dp(6) * 6  # Spacing between 7 tiles (6 gaps)
        
        available_width = hand.width - padding - spacing
        w = max(dp(30), available_width / 7)  # Minimum width of 30dp
        h = w * 2
        return w, h


    @property
    def app(self):
        return MDApp.get_running_app()
