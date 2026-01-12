from kivy.uix.screenmanager import Screen
from kivymd.toast import toast

from models import GameScore


class EditGameScreen(Screen):

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def on_pre_enter(self):
        self.game = self.app.current_game

        if not self.game:
            self.manager.current = "history"
            return

        self.refresh_totals()

    # ======================================================
    # UI
    # ======================================================

    def refresh_totals(self):
        self.ids.totals_box.clear_widgets()

        for name, score in self.game.totals.items():
            self.ids.totals_box.add_widget(
                self._score_label(name, score)
            )

    def _score_label(self, name, score):
        from kivymd.uix.label import MDLabel
        return MDLabel(
            text=f"{name}: {score}",
            halign="center",
        )

    # ======================================================
    # ACTIONS
    # ======================================================

    def add_points(self, name, pts):
        try:
            pts = int(pts)
        except Exception:
            toast("Invalid points")
            return

        self.game.add_points(name, pts)
        self.refresh_totals()

    # ------------------------------------------------------

    def save(self):
        self.app.save_edited_game(self.game)
        toast("Game saved")

    # ------------------------------------------------------

    def cancel(self):
        self.app.current_game = None
        self.manager.current = "history"

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return self.manager.app