from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.toast import toast
from kivy.metrics import dp

import ui_helpers


class GameScreen(MDScreen):

    def on_pre_enter(self):
        self.game = self.app.current_game
        if not self.game:
            self.manager.current = "menu"
            return
        self.refresh_totals()


    def refresh_totals(self):
        box = self.ids.score_box
        box.clear_widgets()
        self.score_inputs = {}
        for name, score in self.app.current_game.totals.items():
            top = MDBoxLayout(orientation="horizontal", size_hint=(0.9, None), height=dp(76), pos_hint = {"center_y":0.5})
            score_field = MDTextField(pos_hint = {"center_y":0.5}, multiline = False, input_filter = "int", hint_text = "Enter Score", on_text_validate = lambda x, n = name: self.add_field_points(n))
            self.score_inputs[name] = score_field
            top.add_widget(MDLabel(text=f"{name} — {score}", font_style="H6"))
            top.add_widget(score_field)
            btns = MDBoxLayout(spacing=dp(10), size_hint=(1, None), height=dp(75))
            for pts in (5, 10, 15, 20, -5):
                btns.add_widget(
                    MDRaisedButton(
                        text=f"{pts:+}", size_hint = (0.2,None), height = dp(60),
                        on_release=lambda x, n=name, p=pts: self.add_points(n, p),))
            btm = MDBoxLayout(size_hint_y=None, height=dp(20))
            btm.add_widget(ui_helpers.MDSeparator())
            box.add_widget(top)
            box.add_widget(btns)
            box.add_widget(btm)


    def add_points(self, name, pts):
        if self.game.finished:
            toast("Game already finished")
            return
        try:
            pts = int(pts)
        except Exception:
            toast("Invalid points")
            return
        # TODO: IF POINTS AREN'T BY 5 = INVALID
        self.game.add_points(name, pts)
        #self.refresh_totals()


    def add_field_points(self, name):
        for n,tf in self.score_inputs.items():
            try:
                new_points = int(self.score_inputs.get(n).text)
            except Exception as e:
                print(e)
                print("skipping player")
                continue
            if new_points % 5 != 0:
                toast("Invalid point value.")
            else:
                self.add_points(n, new_points)
                toast(f"Added {new_points} to {n}'s total")
            self.score_inputs.get(n).text = "0"
        self.refresh_totals()


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
