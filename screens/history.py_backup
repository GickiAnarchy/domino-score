from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem

import models


class HistoryScreen(MDScreen):

    def on_pre_enter(self):
        self.refresh()


    def refresh(self):
        self.ids.history_list.clear_widgets()
      
        games = self.app.games.values()
        if not self.app.games:
            self.ids.history_list.add_widget(
                OneLineListItem(text="No games yet")
            )
            return
        for id,game in self.app.games.items():
            label = self._build_label(game)
            item = OneLineListItem(
                text=label,
                on_release=lambda x, g=game: self.open_game(g),
            )
            self.ids.history_list.add_widget(item)


    def _build_label(self, game: models.GameScore):
        if not game.finished:
            return f"Unfinished game • {game.date[:10]}"
        # 1. Guard against empty games to prevent errors
        if not game.totals:
            return "No Scores"
        # 2. Find the highest score to identify the winner
        # We assume game.totals is a dict like {'PlayerName': int(score)}
        highest_score = max(game.totals.values())
        lbls = []
        for name, score in game.totals.items():
            text_str = f"{name}({score})"
            # 3. Check if this player is the winner (or tied for first)
            if score == highest_score:
                # Apply Markup: Bold ([b]) and Green Color ([color])
                # You can change #00C853 to any hex code you prefer.
                text_str = f"[b][color=#00C853]{text_str}[/color][/b]"
            lbls.append(text_str)
        # 4. Join the items with the pipe separator
        results = " | ".join(lbls)
        return f"{results}  {game.get_date()}"



    def open_game(self, game: models.GameScore):
        self.app.current_game = game
        self.manager.current = "edit"


    @property
    def app(self):
        return MDApp.get_running_app()