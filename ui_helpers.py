from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.boxlayout import MDBoxLayout


class MDSeparator(MDBoxLayout):
    thickness = NumericProperty(dp(1))
    color = ListProperty([1, 1, 1, 0.2])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = self.thickness
        self.md_bg_color = [1, 1, 1, 0.2]


class ConfirmDialog:
    def __init__(
        self,
        title="Are you sure?",
        text="This action cannot be undone.",
        on_confirm=None,
        on_cancel=None,
    ):
        self.on_confirm = on_confirm
        self.on_cancel = on_cancel

        self.dialog = MDDialog(
            title=title,
            text=text,
            buttons=[
                MDFlatButton(
                    text="Cancel",
                    on_release=self._cancel,
                ),
                MDFlatButton(
                    text="Yes",
                    on_release=self._confirm,
                ),
            ],
            auto_dismiss=False,
        )

    def open(self):
        self.dialog.open()

    def dismiss(self):
        self.dialog.dismiss()

    def _confirm(self, *args):
        self.dismiss()
        if self.on_confirm:
            self.on_confirm()

    def _cancel(self, *args):
        self.dismiss()
        if self.on_cancel:
            self.on_cancel()
