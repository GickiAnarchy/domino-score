from kivy.uix.screenmanager import Screen
from kivymd.toast import toast

from models import Player


class PlayersScreen(Screen):

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def on_pre_enter(self):
        self.refresh()

    # ======================================================
    # UI
    # ======================================================

    def refresh(self):
        self.ids.players_list.clear_widgets()

        if not self.app.players:
            from kivymd.uix.list import OneLineListItem
            self.ids.players_list.add_widget(
                OneLineListItem(text="No players yet")
            )
            return

        from kivymd.uix.list import OneLineListItem

        for name in sorted(self.app.players.keys()):
            self.ids.players_list.add_widget(
                OneLineListItem(
                    text=name,
                    on_release=lambda x, n=name: self.select_player(n),
                )
            )

    # ------------------------------------------------------

    def select_player(self, name):
        self.ids.name_input.text = name

    # ======================================================
    # ACTIONS
    # ======================================================

    def add_or_update_player(self):
        name = self.ids.name_input.text.strip()

        if not name:
            toast("Name required")
            return

        players = self.app.players

        # Update existing
        if name in players:
            toast("Player already exists")
            return

        players[name] = Player(name=name)
        self.app.save_players()
        self.refresh()
        self.ids.name_input.text = ""
        toast("Player added")

    # ------------------------------------------------------

    def delete_player(self):
        name = self.ids.name_input.text.strip()

        if name not in self.app.players:
            toast("Select a valid player")
            return

        # Prevent deletion if player exists in games
        for g in self.app.games:
            if name in g.totals:
                toast("Player used in games")
                return

        del self.app.players[name]
        self.app.save_players()
        self.refresh()
        self.ids.name_input.text = ""
        toast("Player deleted")

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return self.manager.app