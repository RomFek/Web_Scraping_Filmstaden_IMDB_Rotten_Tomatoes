import kivy
kivy.require('1.0.7')

from kivy.app import App
from kivy.uix.button import Button


class LauncherGUI(App):

    def build(self):
        # return a Button() as a root widget
        return Button(text='WORK IN PROGRESS')


if __name__ == '__main__':
    LauncherGUI().run()