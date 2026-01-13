from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.toast import toast


class PlayerSelectScreen(MDScreen):

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def on_pre_enter(self):
        self.selected = set()
        self.refresh()

    # ======================================================
    # UI
    # ======================================================

    def refresh(self):
        self.ids.players_box.clear_widgets()

        players = self.app.players

        if not players:
            self.ids.players_box.add_widget(
                MDLabel(
                    text="No players available",
                    halign="center",
                )
            )
            return

        for name in sorted(players.keys()):
            row = MDBoxLayout(
                orientation="horizontal",
                spacing="12dp",
                size_hint_y=None,
                height="48dp",
            )

            checkbox = MDCheckbox()
            checkbox.bind(active=lambda cb, val, n=name: self.toggle(n, val))

            label = MDLabel(text=f"{name}",valign="middle")

            row.add_widget(checkbox)
            row.add_widget(label)
            self.ids.players_box.add_widget(row)

    # ======================================================
    # ACTIONS
    # ======================================================

    def toggle(self, name, active):
        if active:
            self.selected.add(name)
        else:
            self.selected.discard(name)

    # ------------------------------------------------------
    
    def start_game(self):
        selected = list(self.selected)
        if len(selected) < 2:
            toast("Select at least 2 players")
            return
        self.app.start_game(selected)
         
    # ------------------------------------------------------

    def cancel(self):
        self.selected.clear()
        self.manager.current = "menu"

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return MDApp.get_running_app()