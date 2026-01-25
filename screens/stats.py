from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.menu import MDDropdownMenu
from kivymd.toast import toast


class StatsScreen(MDScreen):
    
    def on_pre_enter(self, *args):
        self.menu = None
        self.selected_player = None
        self.refresh_players()
        self.clear_stats()


    def refresh_players(self):
        players = self.app.players
    
        if not players:
            self.ids.player_button.text = "No players"
            self.ids.player_button.disabled = True
            return
        self.ids.player_button.disabled = False
        self.ids.player_button.text = "Select Player"
        top_player = max(players.values(), key = lambda x: x.wins)
        self.ids.top_player_label.text = top_player.name
        items = [
            {
                "text": p,
                "on_release": lambda x=p: self.select_player(x),
            }
            for p in sorted(players, key=lambda p: p.lower())
        ]
        if self.menu:
            self.menu.dismiss()
        self.menu = MDDropdownMenu(
            caller=self.ids.player_button,
            items=items,
            width_mult=4,)


    def clear_stats(self):
        self.ids.wins.text = "Wins: —"
        self.ids.losses.text = "Losses: —"
        self.ids.games.text = "Games Played: —"
        self.ids.winrate.text = "Win Rate: —"
        self.ids.highscore.text = "Highest Score: —"


    def select_player(self, name):
        self.selected_player = name
        self.ids.player_button.text = name
        self.menu.dismiss()
        self.refresh_stats()


    def refresh_stats(self):
        name = self.selected_player
        if not name:
            return
        try:
            player = self.app.players.get(name)
        except Exception as e:
            print("ERROR IN STATS -> REFRESH_STATS")
            print(e)
        if not player:
            toast("Player not found")
            self.clear_stats()
            return
        wins = player.wins
        losses = player.losses
        games = wins + losses
        h_score = player.highest_score
        rate = f"{(wins / games * 100):.1f}%" if games else "0%"
        self.ids.wins.text = f"Wins: {wins}"
        self.ids.losses.text = f"Losses: {losses}"
        self.ids.games.text = f"Games Played: {games}"
        self.ids.winrate.text = f"Win Rate: {rate}"
        self.ids.highscore.text = f"Highest Score: {h_score}"


    def open_menu(self):
        if self.menu:
            self.menu.open()


    @property
    def app(self):
        return MDApp.get_running_app()