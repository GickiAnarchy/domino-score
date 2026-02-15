from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ListProperty
from kivymd.uix.screen import MDScreen

# We define the look in KV for stability and performance
KV = '''
<DominoTile>:
    size_hint: None, None
    size: 100, 200
    canvas.before:
        # Background
        Color:
            rgba: self.tile_color
        RoundedRectangle:
            pos: 0, 0
            size: self.size
            radius: [dp(10)]
        
        # Divider Line
        Color:
            rgba: 0.5, 0.5, 0.5, 1
        Line:
            points: [self.width * 0.1, self.height / 2, self.width * 0.9, self.height / 2]
            width: 1.1

    # We will use a separate method to handle the dots (pips) 
    # as they are dynamic based on the value.
'''

class DominoTile(RelativeLayout):
    value_top = NumericProperty(0)
    value_bottom = NumericProperty(0)
    tile_color = ListProperty([1, 1, 1, 1])
    pip_color = ListProperty([0, 0, 0, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Bind values so pips redraw when numbers change
        self.bind(value_top=self.draw_all_pips, 
                  value_bottom=self.draw_all_pips,
                  size=self.draw_all_pips)

    def draw_all_pips(self, *args):
        # We use canvas.after for pips so they stay on top
        self.canvas.after.clear()
        if self.width <= 1: return # Safety check for Pydroid
        
        with self.canvas.after:
            from kivy.graphics import Color
            Color(*self.pip_color)
            self._draw_half_pips(self.value_top, is_top=True)
            self._draw_half_pips(self.value_bottom, is_top=False)

    def _draw_half_pips(self, value, is_top=True):
        from kivy.graphics import Ellipse
        pad = self.width * 0.22
        m_x = self.width / 2
        offset_y = self.height / 2 if is_top else 0
        m_y = offset_y + (self.height / 4)
        
        p_size = self.width * 0.16
        r = p_size / 2
        l, r_side = pad, self.width - pad
        b, t = offset_y + pad, offset_y + (self.height / 2) - pad

        coords = []
        if value % 2 == 1: coords.append((m_x, m_y))
        if value >= 2: coords.extend([(l, t), (r_side, b)])
        if value >= 4: coords.extend([(r_side, t), (l, b)])
        if value == 6: coords.extend([(l, m_y), (r_side, m_y)])

        for x, y in coords:
            Ellipse(pos=(x - r, y - r), size=(p_size, p_size))

class MainApp(MDApp):
    def build(self):
        Builder.load_string(KV)
        screen = MDScreen()
        
        # Testing a 5-2 domino
        tile = DominoTile()
        tile.value_top = 5
        tile.value_bottom = 2
        tile.pos_hint = {"center_x": 0.5, "center_y": 0.5}
        
        screen.add_widget(tile)
        return screen

if __name__ == "__main__":
    MainApp().run()
