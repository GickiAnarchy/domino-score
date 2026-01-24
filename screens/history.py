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
        winner = game.winner or "?"
        high = max(game.totals.values()) if game.totals else 0
        return f"{winner} won ({high}) • {game.date[:10]}"


    def open_game(self, game: models.GameScore):
        self.app.current_game = game
        self.manager.current = "edit"


    def delete_game(self, game_id):
        before = len(self.app.games)
        self.app.games = [
            g for g in self.app.games if g.id != game_id]
        if len(self.app.games) < before:
            self.app.save_games()
            self.app.sync_players_from_games()
            self.refresh()
            print("Game deleted")
        else:
            print("Game not found")


    @property
    def app(self):
        return MDApp.get_running_app()