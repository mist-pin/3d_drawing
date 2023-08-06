from kivy.core.window import Window
from kivy.uix.screenmanager import FadeTransition
from kivymd.app import MDApp
from kivymd.uix.screenmanager import MDScreenManager

from login_signup import login
from draw_shape import drawing


class PageHandler(MDScreenManager):
    def __init__(self):
        super().__init__()
        self.add_widget(drawing.DrawScreen(name='DrawScreen'))
        self.current = 'DrawScreen'
        self.add_widget(login.GetData(name='GetData'))
        # self.current = 'GetData'
        self.transition = FadeTransition()
        self.add_widget(login.VerifyData(name='VerifyData'))
        # self.current = 'VerifyData'


class MyApp(MDApp):
    def build(self):
        Window.size = (450, 950)
        self.theme_cls.primary_palette = 'Yellow'
        self.theme_cls.theme_style = 'Dark'
        return PageHandler()


MyApp().run()
