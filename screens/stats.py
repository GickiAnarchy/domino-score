from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast


class StatsScreen(MDScreen):

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def on_pre_enter(self):
        self.menu = None
        self.selected_player = None
        self.refresh_players()
        self.clear_stats()

    # ======================================================
    # UI
    # ======================================================

    def refresh_players(self):
        players = list(self.app.players.keys())

        if not players:
            self.ids.player_button.text = "No players"
            self.ids.player_button.disabled = True
            return

        self.ids.player_button.disabled = False
        self.ids.player_button.text = "Select Player"

        items = [
            {
                "text": name,
                "on_release": lambda x=name: self.select_player(x),
            }
            for name in sorted(players)
        ]

        if self.menu:
            self.menu.dismiss()

        self.menu = MDDropdownMenu(
            caller=self.ids.player_button,
            items=items,
            width_mult=4,
        )

    # ------------------------------------------------------

    def open_menu(self):
        if self.menu:
            self.menu.open()

    # ------------------------------------------------------

    def select_player(self, name):
        self.selected_player = name
        self.ids.player_button.text = name
        self.menu.dismiss()
        self.refresh_stats()

    # ------------------------------------------------------

    def clear_stats(self):
        self.ids.wins.text = "Wins: —"
        self.ids.losses.text = "Losses: —"
        self.ids.games.text = "Games Played: —"
        self.ids.winrate.text = "Win Rate: —"

    # ------------------------------------------------------

    def refresh_stats(self):
        name = self.selected_player
        if not name:
            return

        player = self.app.players.get(name)
        if not player:
            toast("Player not found")
            self.clear_stats()
            return

        wins = player.wins
        losses = player.losses
        games = wins + losses

        rate = f"{(wins / games * 100):.1f}%" if games else "0%"

        self.ids.wins.text = f"Wins: {wins}"
        self.ids.losses.text = f"Losses: {losses}"
        self.ids.games.text = f"Games Played: {games}"
        self.ids.winrate.text = f"Win Rate: {rate}"

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return MDApp.get_running_app()