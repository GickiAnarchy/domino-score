from kivy.core.clipboard import Clipboard
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.screen import MDScreen




class ExportScreen(MDScreen):
    
    def on_pre_enter(self):
        self.ex_label = self.ids.export_label
        self.data = self.app.format_data_for_export()
        if self.data is None:
            self.ex_label.text = "Error in exporting data."
            self.ids.copy_button.disabled = True
        else:
            self.ids.copy_button.disabled = False
            self.ex_label.text = "Data ready to copy./nPress button to copy data."


    def copy_data(self):
        Clipboard.copy(self.data)


    @property
    def app(self):
        return MDApp.get_running_app()