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
    pass