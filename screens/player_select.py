from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.selectioncontrol import MDCheckbox
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.toast import toast
from kivy.properties import ListProperty


class PlayerSelectScreen(MDScreen):
    selected = ListProperty([])
    
    def on_enter(self):
        self.selected = []


    def refresh(self):
        players = self.app.players
        self.ids.player_box.clear_widgets()
        if not players:
            self.ids.players_box.add_widget(
                MDLabel(
                    text="No players available",
                    halign="center",))
            return
        for pn,p in players.items():
            name = pn
            row = MDBoxLayout(
                orientation="horizontal",
                spacing="12dp",
                size_hint_y=None,
                height="48dp",
            )
            checkbox = MDCheckbox()
            checkbox.bind(
                active=lambda cb, val, n=name: self.toggle(n, val)
            )
            label = MDLabel(
                text=name,
                valign="middle",
            )
            row.add_widget(checkbox)
            row.add_widget(label)
            self.ids.players_box.add_widget(row)


    def toggle(self, name, active):
        if active:
            if name not in self.selected:
                self.selected.append(name) # Use append for lists
        else:
            if name in self.selected:
                self.selected.remove(name) # Use remove for lists

    
    def start_game(self):
        selected = list(self.selected)
        if len(selected) < 2:
            toast("Select at least 2 players")
            return
        #self.app.start_game(selected)


    def cancel(self):
        self.selected.clear()
        self.manager.current = "menu"


    def delete(self):
        selected = list(self.selected)
        for s in selected:
            self.app.delete_player(s)
        self.refresh()


    @property
    def app(self):
        return MDApp.get_running_app()