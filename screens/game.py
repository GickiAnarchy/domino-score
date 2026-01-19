
from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.metrics import dp

from ui_helpers import MDSeparator



class GameScreen(MDScreen):

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def on_pre_enter(self):
        self.game = self.app.current_game

        if not self.game:
            self.manager.current = "menu"
            return

        self.refresh_totals()

    # ======================================================
    # UI
    # ======================================================

    def refresh_totals(self):
        box = self.ids.score_box
        box.clear_widgets()
        
        self.score_inputs = {}

        for name, score in self.app.current_game.totals.items():
            top = MDBoxLayout(orientation="horizontal", size_hint=(0.9, None), height=dp(76), pos_hint = {"center_y":0.5})
            score_field = MDTextField(pos_hint = {"center_y":0.5}, multiline = False, input_filter = "int", hint_text = "Enter Score", on_text_validate = lambda x, n = name: self.add_field_points(n))
            self.score_inputs[name] = score_field
            top.add_widget(MDLabel(text=f"{name} — {score}", font_style="H6"))
            top.add_widget(score_field)
            
            btns = MDBoxLayout(spacing=dp(15), size_hint=(0.9, None), height=dp(70))
            for pts in (5, 10, 20, -5):
                btns.add_widget(
                    MDRaisedButton(
                        text=f"{pts:+}", size_hint_y = None, height = dp(45),
                        on_release=lambda x, n=name, p=pts: self.add_points(n, p),))
            
            btm = MDBoxLayout(size_hint_y=None, height=dp(20))
            btm.add_widget(MDSeparator())
            
            box.add_widget(top)
            box.add_widget(btns)
            box.add_widget(btm)
            
        
    # ======================================================
    # ACTIONS
    # ======================================================

    def add_points(self, name, pts):
        if self.game.finished:
            toast("Game already finished")
            return
        try:
            pts = int(pts)
        except Exception:
            toast("Invalid points")
            return
        # TODO: IF POINTS AREN'T BY 5 = INVALID
        self.game.add_points(name, pts)
        self.refresh_totals()

    # ------------------------------------------------------
    
    def finish_game(self):
        self.game.finish_game()
        self.app.end_game()
        self.manager.current = "menu"
    
    # ------------------------------------------------------

    def cancel_game(self):
        self.app.current_game = None
        self.manager.current = "menu"


    def add_field_points(self, name):
        field = self.score_inputs.get(name)
        if not field or not field.text:
            print("Text fields is empty or invalid")
            return
        try:
            new_points = int(field.text)
            self.add_points(name, new_points)
            toast(f"Added {new_points} to {name}'s total")
            field.text = ""
            self.refresh_totals()
        except ValueError as e:
            print(e)
            toast("Please enter a valid number")

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return MDApp.get_running_app()