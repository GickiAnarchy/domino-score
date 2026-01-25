from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivymd.uix.pickers import MDDatePicker, MDTimePicker
from datetime import datetime

import models
import ui_helpers



class EditGameScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.game = self.app.current_game
        container = self.ids.players_container
        
        # 1. Clear any old fields from previous edits
        container.clear_widgets()
        self.player_fields = {} # To keep track of the new widgets

        if not self.game:
            return

        # 2. Set the date field
        self.current_dt = datetime.fromisoformat(self.game.date)
        self.update_date_display()

        # 3. Create a TextField for every player in this game
        for player_name, score in self.game.totals.items():
            field = MDTextField(
                text=str(score),
                hint_text=f"{player_name}'s Score",
                mode="line",
                input_filter="int"
            )
            container.add_widget(field)
            # Store the widget reference so we can read it later
            self.player_fields[player_name] = field


    def update_date_display(self):
        # Update the text field with a pretty format (e.g., "01/25/26 09:30AM")
        self.ids.date_field.text = self.current_dt.strftime("%m/%d/%y %I:%M%p")


    def save_changes(self):
        game = self.game        
        # Update scores from the text fields
        for name, field in self.player_fields.items():
            try:
                game.totals[name] = int(field.text)
            except ValueError:
                game.totals[name] = 0        
        game.date = self.current_dt.isoformat()
        # Save to disk
        self.app.add_game(game)
        self.manager.current = "history"


    def show_datetime_dialog(self):
        self.edited_dt = self.current_dt
        self.show_date_picker()
        self.show_time_picker()
        self.current_dt = self.edited_dt
        self.update_date_display()

    def show_date_picker(self):
        date_dialog = MDDatePicker()
        date_dialog.bind(on_save=self.on_date_save)
        date_dialog.open()


    def on_date_save(self, instance, value, date_range):
        self.edited_dt = datetime.combine(value, self.current_dt.time())


    def show_time_picker(self):
        time_dialog = MDTimePicker(year=self.current_dt.year,month=self.current_dt.month,day=self.current_dt.day)
        time_dialog.bind(on_save=self.on_time_save)
        time_dialog.open()
    
    
    def on_time_save(self, instance, value, time_range):
        self.edited_dt = datetime.combine(self.current_dt.date(), value)


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


    def add_points(self, name, pts):
        try:
            pts = int(pts)
        except Exception:
            toast("Invalid points")
            return

        self.game.add_points(name, pts)
        self.refresh_totals()


    def save(self):
        self.app.save_edited_game(self.game)
        toast("Game saved")


    def cancel(self):
        self.app.current_game = None
        self.manager.current = "history"
    
    
    def delete(self):
        self.app.delete_game(self.game)
        self.manager.current = "menu"

    @property
    def app(self):
        return MDApp.get_running_app()
