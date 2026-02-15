from kivymd.app import MDApp
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.properties import NumericProperty, ListProperty
from kivy.graphics import Color, Ellipse, Line
from kivy.animation import Animation
from kivymd.uix.screen import MDScreen


class GameBoard(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(0.2, 0.2, 0.2, 1) # Dark grey lines
            grid_size = 80 # Must match DominoTile.grid_size
            # Draw vertical lines
            for x in range(0, 2000, grid_size):
                Line(points=[x, 0, x, 2000], width=1)
            # Draw horizontal lines
            for y in range(0, 2000, grid_size):
                Line(points=[0, y, 2000, y], width=1)
