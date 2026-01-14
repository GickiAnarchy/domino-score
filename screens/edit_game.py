from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivymd.uix.pickers import MDDatePicker
from datetime import datetime

from models import GameScore


class EditGameScreen(MDScreen):

    # ======================================================
    # LIFECYCLE
    # ======================================================

    def on_pre_enter(self):
        self.app = MDApp.get_running_app()
        self.game = self.app.current_game
        container = self.ids.players_container
        
        # 1. Clear any old fields from previous edits
        container.clear_widgets()
        self.player_fields = {} # To keep track of the new widgets

        if not self.game:
            return

        # 2. Set the date field
        self.ids.date_field.text = str(self.game.date)

        # 3. Create a TextField for every player in this game
        for player_name, score in self.game.scores.items():
            field = MDTextField(
                text=str(score),
                hint_text=f"{player_name}'s Score",
                mode="outline",
                input_filter="int"
            )
            container.add_widget(field)
            # Store the widget reference so we can read it later
            self.player_fields[player_name] = field

    def save_changes(self):
        game = self.game        
        # Update scores from the text fields
        for name, field in self.player_fields.items():
            try:
                game.scores[name] = int(field.text)
            except ValueError:
                game.scores[name] = 0        
        game.date = self.ids.date_field.text
        # Save to disk
        self.app.save_edited_game(game)
        self.app.current_game = None
        toast("Changes saved!")
        self.manager.current = "history"
        
    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()

    def on_date_save(self, instance, value, date_range):
        self.ids.date_field.text = str(value)

    #def save_changes(self):
#        if not self.app.current_game:
#            return

#        try:
#            # Update the object in memory
#            self.app.current_game.player_name = self.ids.player_name_field.text
#            self.app.current_game.score = int(self.ids.score_field.text)
#            self.app.current_game.date = self.ids.date_field.text
#            
#            # Save to file (using your existing util function)
#            save_games(self.app.games_file, self.app.games)
#            
#            toast("Game updated successfully")
#            self.manager.current = "history"
#        except ValueError:
#            toast("Please enter a valid number for score")

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
        return MDTextField(
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
    
    # ------------------------------------------------------
    
    def delete(self):
        self.app.delete_game(self.game)
        self.manager.current = "history"

    # ======================================================
    # UTIL
    # ======================================================

    @property
    def app(self):
        return MDApp.get_running_app()