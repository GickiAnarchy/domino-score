from kivymd.app import MDApp
from kivy.uix.scatter import Scatter
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ListProperty, ObjectProperty 
from kivy.graphics import Color, Ellipse, Line, Rectangle
from kivy.animation import Animation
from kivymd.uix.screen import MDScreen
from kivy.metrics import dp
from kivy.animation import Animation
from kivymd.uix.screenmanager import MDScreenManager
from kivymd.uix.widget import Widget
import models




class MyScreenManager(MDScreenManager):
    pass



class DominoTileWidget(Scatter):
    """
    A draggable domino tile widget using Scatter behavior.
    DEBUG VERSION - prints debug info.
    """
    value_top = NumericProperty(0)
    value_bottom = NumericProperty(0)
    tile_color = ListProperty([1, 1, 1, 1])
    pip_color = ListProperty([0, 0, 0, 1])
    model = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Disable rotation to keep tiles vertically aligned
        self.do_rotation = False
        self.size_hint = (None, None)
        
        print(f"DominoTile created: top={self.value_top}, bottom={self.value_bottom}, size={self.size}")
        
        # Redraw pips whenever the value or size changes
        self.bind(
            size=self.draw_all_pips,
            value_top=self.draw_all_pips,
            value_bottom=self.draw_all_pips
        )
        
        # Force initial pip draw after widget is fully initialized
        from kivy.clock import Clock
        Clock.schedule_once(self.draw_all_pips, 0)

    def draw_all_pips(self, *args):
        # Clear previous canvas instructions
        self.canvas.after.clear()
        
        print(f"draw_all_pips called: size={self.size}, top={self.value_top}, bottom={self.value_bottom}")
        
        # Safety check for widget initialization
        if self.width <= 1 or self.height <= 1:
            print(f"  Skipping - size too small")
            return

        # Draw pips in canvas.after so they appear on top of background
        with self.canvas.after:
            # DEBUG: Draw a colored border to verify canvas is working
            Color(1, 0, 0, 1)  # Red border
            Line(rectangle=(0, 0, self.width, self.height), width=2)
            
            # Set pip color (black dots)
            Color(*self.pip_color)
            
            # Draw pips for top half
            pip_count_top = self._draw_half_pips(self.value_top, is_top=True)
            print(f"  Drew {pip_count_top} pips for top half (value={self.value_top})")
            
            # Draw pips for bottom half
            pip_count_bottom = self._draw_half_pips(self.value_bottom, is_top=False)
            print(f"  Drew {pip_count_bottom} pips for bottom half (value={self.value_bottom})")
            
            # Draw divider line between halves
            Color(0.3, 0.3, 0.3, 1)
            Line(points=[self.width * 0.1, self.height / 2, 
                        self.width * 0.9, self.height / 2], 
                 width=1.5)

    def _draw_half_pips(self, value, is_top=True):
        """
        Draw pips for one half of the domino.
        Returns the number of pips drawn.
        """
        if value == 0:
            return 0  # No pips for 0
            
        # Geometric calculations for pip placement
        pad = self.width * 0.22
        m_x = self.width / 2
        offset_y = self.height / 2 if is_top else 0
        m_y = offset_y + (self.height / 4)
        
        p_size = self.width * 0.16
        r = p_size / 2
        l = pad
        r_side = self.width - pad
        b = offset_y + pad
        t = offset_y + (self.height / 2) - pad

        # Standard Domino pip patterns (1-6)
        coords = []
        if value == 1:
            coords = [(m_x, m_y)]
        elif value == 2:
            coords = [(l, t), (r_side, b)]
        elif value == 3:
            coords = [(l, t), (m_x, m_y), (r_side, b)]
        elif value == 4:
            coords = [(l, t), (r_side, t), (l, b), (r_side, b)]
        elif value == 5:
            coords = [(l, t), (r_side, t), (m_x, m_y), (l, b), (r_side, b)]
        elif value == 6:
            coords = [(l, t), (l, m_y), (l, b), (r_side, t), (r_side, m_y), (r_side, b)]

        # Create Ellipse graphics for each pip
        for x, y in coords:
            Ellipse(pos=(x - r, y - r), size=(p_size, p_size))
        
        return len(coords)

    def on_touch_up(self, touch):
        # Check if the touch release occurred within the tile's area
        if self.collide_point(*touch.pos):
            # Direct access via MDApp.get_running_app()
            app = MDApp.get_running_app()
            try:
                # Find the BoardScreen in the ScreenManager
                board_screen = app.root.get_screen('board')
                if board_screen and self.model:
                    board_screen.play_tile(self.model)
            except Exception as e:
                print(f"Interaction Error: {e}")
            return True
        return super().on_touch_up(touch)
