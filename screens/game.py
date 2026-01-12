from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.toast import toast


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
        self.ids.score_box.clear_widgets()

        from kivymd.uix.label import MDLabel

        for name, score in self.game.totals.items():
            self.ids.score_box.add_widget(
                MDLabel(
                    text=f"{name}: {score}",
                    halign="center",
                )
            )

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
        if not self.game.totals:
            toast("No scores yet")
            return
    
        result = self.game.end_hand()
    
        if result == "win":
            toast(f"{self.game.winner} wins!")
            self.app.archive_game(self.game)
            self.manager.current = "menu"
    
        elif result == "tie":
            toast("Tie at the top — another hand!")
    
        else:
            toast("Hand completed.")
    
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