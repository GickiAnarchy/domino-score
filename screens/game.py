from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.metrics import dp
from kivy.properties import ObjectProperty

import ui_helpers




class GameScreen(MDScreen):
    game = ObjectProperty(None)
    score_inputs = {}
    score_labels = {}


    def on_pre_enter(self):
        self.game = self.app.current_game
        if not self.game:
            if hasattr(self.manager, 'current'):
                self.manager.current = "menu"
            return
        self.refresh_totals()


    def refresh_totals(self):
        """
        Builds ONLY the player rows. 
        The 'End Round' button is now handled by the KV file.
        """
        box = self.ids.score_box
        box.clear_widgets()
        
        self.score_inputs = {}
        self.score_labels = {}

        for name, score in self.app.current_game.totals.items():
            # 1. Player Container
            player_card = MDBoxLayout(
                orientation="vertical", 
                size_hint_y=None, 
                height=dp(130), # Reduced height slightly
                padding=[0, 0, 0, dp(10)]
            )
            
            # 2. Name and Input Row
            top = MDBoxLayout(orientation="horizontal", size_hint=(1, None), height=dp(60))
            
            score_label = MDLabel(
                text=f"{name}: {score}", 
                font_style="H6",
                halign="left",
                theme_text_color="Primary",
                size_hint_x=0.6
            )
            self.score_labels[name] = score_label
            
            score_field = MDTextField(
                text="0",
                mode="rectangle",
                pos_hint={"center_y": 0.5},
                size_hint_x=0.4,
                input_filter="int",
                hint_text="Add",
            )
            self.score_inputs[name] = score_field
            
            top.add_widget(score_label)
            top.add_widget(score_field)
            
            # 3. Calculator Buttons Row
            btns = MDBoxLayout(spacing=dp(5), size_hint=(1, None), height=dp(50))
            
            # Values for the buttons
            point_values = [5, 10, 15, 20, -5]
            
            for pts in point_values:
                # Color logic: Red for negative, Primary for positive
                color = self.app.theme_cls.primary_color if pts > 0 else [0.8, 0, 0, 1]
                
                btns.add_widget(
                    MDRaisedButton(
                        text=f"{pts:+}", 
                        size_hint=(0.2, 1), 
                        md_bg_color=color,
                        elevation=0, # Flat look for calc buttons
                        on_release=lambda x, n=name, p=pts: self.update_input_field(n, p)
                    )
                )

            player_card.add_widget(top)
            player_card.add_widget(btns)
            
            # 4. Add separator
            try:
                sep = ui_helpers.MDSeparator()
            except:
                from kivymd.uix.card import MDSeparator
                sep = MDSeparator(height=dp(1))
            
            box.add_widget(player_card)
            box.add_widget(sep)


    def update_input_field(self, name, points):
        """Updates the textfield value (Calculator logic)."""
        if self.game.finished:
            toast("Game is finished")
            return

        field = self.score_inputs.get(name)
        if not field: return

        try:
            current_val = int(field.text) if field.text else 0
            new_val = current_val + int(points)
            field.text = str(new_val)
        except ValueError:
            field.text = str(points)


    def commit_round(self):
        """Triggered by the KV button 'END ROUND'."""
        if self.game.finished:
            toast("Game is finished.")
            return

        changes_made = False

        for name, field in self.score_inputs.items():
            try:
                round_points = int(field.text)
            except ValueError:
                round_points = 0
            
            if round_points != 0:
                # Update Game Data
                current_total = self.app.current_game.totals.get(name, 0)
                self.app.current_game.totals[name] = current_total + round_points
                
                # Update Label
                if name in self.score_labels:
                    self.score_labels[name].text = f"{name}: {self.app.current_game.totals[name]}"
                
                # Reset Field
                field.text = "0"
                changes_made = True

        if changes_made:
            toast("Scores updated!")
        else:
            toast("No points entered.")


    def finish_game(self):
        print("GameScreen -> finish_game()")
        def _do_finish_game():
            self.game.finish_game()
            self.app.end_game()
            self.manager.current = "menu"
        self.finish_comfirm = ui_helpers.ConfirmDialog(title="Finish this game?", text=f"Are you sure you want to finalize this game?\n\nWinner: {self.game.winner}",on_confirm=_do_finish_game)
        self.finish_comfirm.open()



    def cancel_game(self):
        self.app.current_game = None
        self.manager.current = "menu"


    @property
    def app(self):
        return MDApp.get_running_app()
