from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem
from kivymd.toast import toast

from models import GameScore


class HistoryScreen(MDScreen):

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def on_pre_enter(self):
        self.refresh()

    # ======================================================
    # UI
    # ======================================================

    def refresh(self):
        self.ids.history_list.clear_widgets()

        app = self.app
        games = sorted(
            app.games,
            key=lambda g: g.date,
            reverse=True
        )

        if not games:
            self.ids.history_list.add_widget(
                OneLineListItem(text="No games yet")
            )
            return

        for game in games:
            label = self._build_label(game)
            item = OneLineListItem(
                text=label,
                on_release=lambda x, g=game: self.open_game(g),
            )
            self.ids.history_list.add_widget(item)

    # ------------------------------------------------------

    def _build_label(self, game: GameScore):
        if not game.finished:
            return f"Unfinished game • {game.date[:10]}"

        winner = game.winner or "?"
        high = max(game.totals.values()) if game.totals else 0
        return f"{winner} won ({high}) • {game.date[:10]}"

    # ======================================================
    # ACTIONS
    # ======================================================

    def open_game(self, game: GameScore):
        self.app.current_game = game
        self.manager.current = "edit"

    # ------------------------------------------------------

    def delete_game(self, game_id):
        before = len(self.app.games)

        self.app.games = [
            g for g in self.app.games if g.id != game_id]

        if len(self.app.games) < before:
            self.app.save_games()
            self.app.sync_players_from_games()
            self.refresh()
            toast("Game deleted")
        else:
            toast("Game not found")

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return MDApp.get_running_app()