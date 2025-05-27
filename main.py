from classes.application import App

from ui.ui import UI


if __name__ == "__main__":
    app = App.get_or_init("habits.json")
    ui = UI(app)
    ui.main_loop()
