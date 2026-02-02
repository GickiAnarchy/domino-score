from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.list import OneLineListItem

import utils


class ImportScreen(MDScreen):

    #def on_pre_enter(self):
#        self.refresh()
#    
#    
#    def refresh(self):
#        self.ids.import_list.clear_widgets()
#        dates = utils.get_export_dates()
#        exported_data = utils.get_data()
#        if not dates:
#            self.ids.import_list.add_widget(OneLineListItem(text="No exported data"))
#            return
#        i = 0
#        for date,data  in exported_data.items():
#            label = self._build_label(date)
#            item = OneLineListItem(text = label, on_release = lambda x, d = date: self.import_date(d),)
#            self.ids.import_list.add_widget(item)
#            i += 1
#            if i == 5:
#                break


#    def _build_label(self, date):
#            if not date:
#                return "Error"
#            return f"{date}"


    def import_data(self, data):
        self.app.import_data(data)


    @property
    def app(self):
        return MDApp.get_running_app()