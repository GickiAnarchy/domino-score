from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen
from kivymd.toast import toast


class PlayerSelectScreen(Screen):

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
            from kivymd.uix.label import MDLabel
            self.ids.players_box.add_widget(
                MDLabel(
                    text="No players available",
                    halign="center",
                )
            )
            return

        from kivymd.uix.selectioncontrol import MDCheckbox
        from kivymd.uix.label import MDLabel
        from kivymd.uix.boxlayout import MDBoxLayout

        for name in sorted(players.keys()):
            row = MDBoxLayout(
                orientation="horizontal",
                spacing="12dp",
                size_hint_y=None,
                height="48dp",
            )

            checkbox = MDCheckbox(
                on_active=lambda cb, val, n=name: self.toggle(n, val)
            )

            label = MDLabel(
                text=name,
                valign="middle",
            )

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
        if len(self.selected) < 2:
            toast("Select at least 2 players")
            return

        self.app.start_game(list(self.selected))

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