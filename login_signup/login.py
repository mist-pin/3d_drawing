import sys

from kivy.uix.screenmanager import FadeTransition
from kivymd.uix.screen import MDScreen


class GetData(MDScreen):
    font_s = None

    def __init__(self, **kwargs):
        self.font_s = self.size[1] / 3.5
        super().__init__(**kwargs)

    def next_button_pressed(self, *args):
        self.manager.current = 'VerifyData'


class VerifyData(MDScreen):
    def validate(self, otp):
        if len(otp) == 4:
            self.manager.transition = FadeTransition()
            self.manager.current = 'GetData'
