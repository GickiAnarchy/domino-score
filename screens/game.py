from ui_helpers import MDSeparator

from kivymd.app import MDApp
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.toast import toast
from kivy.metrics import dp



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

        for name, score in self.app.current_game.totals.items():
            top = MDBoxLayout(orientation="horizontal", size_hint=(0.9, None), height=dp(40))
            top.add_widget(MDLabel(text=f"{name} — {score}", font_style="H6"))
            btns = MDBoxLayout(spacing=dp(15), size_hint=(0.9, None), height=dp(50))
            for pts in (5, 10, 20, -5):
                btns.add_widget(
                    MDRaisedButton(
                        text=f"{pts:+}",
                        on_release=lambda x, n=name, p=pts: self.add_points(n, p),))
            box.add_widget(top)
            box.add_widget(btns)
            box.add_widget(MDSeparator(thickness=dp(5)))
        # Provisional winner notice
        if self.game.max_reached:
            leader = self.game.provisional_leader
            toast(f"Possible winner: {leader}")

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
        self.game.add_points(name, pts)
        self.refresh_totals()

    # ------------------------------------------------------
    
    def finish_game(self):
        self.app.end_current_game()
    
    # ------------------------------------------------------

    def cancel_game(self):
        self.app.current_game = None
        self.manager.current = "menu"

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return MDApp.get_running_app()