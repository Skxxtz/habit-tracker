import os
import sys
import select
import array

from typing import Optional

from classes.application import App
from constants import CLEAR_SCREEN, CURSOR_HOME, DEBUG, HIDE_CURSOR, SHOW_CURSOR
from helpers.text import bold, bold_underline
from ui.classes.submenu import ConfirmSubmenu, Submenu

# Necessary imports for windows and unix
if os.name == "nt":
    import msvcrt
else:
    import fcntl
    import tty
    import termios


class UI:
    submenu: Optional[Submenu]
    app: App
    index: int

    def __init__(self, app: App) -> None:
        self.app = app
        self.index = 0
        self.submenu = None
        UiHelpers.draw_list(self.app, self.index)

    def main_loop(self) -> None:
        """
        This method is the mainloop for the ui. In it, it will wait for a user
        input and execute the requested action

        Args:
            self (UI)
        Returns:
            None
        """
        try:
            while True:
                key = self.get_keypress()
                _break = self.eval_action(key)
                if _break:
                    break
        finally:
            print(SHOW_CURSOR, end="", flush=True)

    def get_keypress(self) -> Optional[str]:
        """
        For windows:
        This method reads the current keypress from stdin
        For Unix:
        This method first blockingly polls the stdin file descriptor. Then it returns the evaluated key

        Args:
            self (UI)
        Returns:
            event (Optional[str]): The evaluated event or the key pressed. Can be none
        """
        if os.name == "nt":
            if msvcrt.kbhit():
                ch = msvcrt.getch()
                if not ch:
                    return

                if ch == b"\x1b":
                    return "ESCAPE"
                elif ch == b"\xe0":  # Special key prefix
                    ch2 = msvcrt.getch()
                    if ch2 == b"H":
                        return "UP"
                    elif ch2 == b"P":
                        return "DOWN"
                elif ch == b"\r":
                    return "RETURN"
                elif ch == b"k":
                    return "UP"
                elif ch == b"j":
                    return "DOWN"
                elif ch == b"q":
                    return "QUIT"
                elif ch == b"\x0c":
                    return "CLEAR_SCREEN"
                else:
                    return ch.decode("utf-8")
        else:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                # Preserve ctrl-c capabilities
                tty.setcbreak(fd)

                # poll file descriptor for stdin blockingly for efficiency
                _, _, _ = select.select([sys.stdin], [], [])
                num_bytes = UiHelpers.get_available_bytes(fd)
                chars = sys.stdin.read(num_bytes)

                match chars:
                    case "\x1b":
                        return "ESCAPE"
                    case "\n" | "\r":
                        return "RETURN"
                    case "q":
                        return "QUIT"
                    case "\x0c":
                        return "CLEAR_SCREEN"

                    # Navigation
                    case "\x1b[A" | "k":
                        return "UP"
                    case "\x1b[B" | "j":
                        return "DOWN"

                    # Return keys
                    case _:
                        return chars
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    def eval_action(self, action: Optional[str]) -> Optional[bool]:
        """
        This method binds a keypress event to an internal action. For example,
        it handles nacigation or habit completion.

        Args:
            self (UI)
            action (Optional[str]): Takes the output from self.get_keypress

        Returns:
            _break (Optional[bool]): In some cases, we want to terminate the
            app mainloop, this parameter is used to controll this behavior
        """
        if not action:
            return False

        match action:
            case "UP":
                if self.submenu:
                    self.submenu.up()
                    self.submenu.refresh()
                else:
                    filter_len = len(self.app.filter.tmp)
                    if not filter_len == 0:
                        self.index = (self.index - 1) % filter_len
                        UiHelpers.draw_list(self.app, self.index)

            case "DOWN":
                if self.submenu:
                    self.submenu.down()
                    self.submenu.refresh()
                else:
                    filter_len = len(self.app.filter.tmp)
                    if not filter_len == 0:
                        self.index = (self.index + 1) % filter_len
                        UiHelpers.draw_list(self.app, self.index)

            case "RETURN":
                if self.submenu:
                    self.submenu.activate()
                    self.submenu = None
                    UiHelpers.draw_list(self.app, self.index)

            case "ESCAPE":
                if self.submenu:
                    self.submenu = None
                    UiHelpers.draw_list(self.app, self.index)

            case "c":
                selected = self.app.habit_at_index(self.index)
                if not selected:
                    return
                selected.toggle_completed()
                self.app.filter.apply_filter()
                UiHelpers.draw_list(self.app, self.index)
                self.app.save()

            case "o":
                print(SHOW_CURSOR + CLEAR_SCREEN + CURSOR_HOME, end="")
                print(
                    "To exit press <Return> and then <Esc> once you're in the interval selection"
                )
                name = input("Habit name:\n")

                # callback function to add a new habit
                def on_confirm(option: str):
                    opt = option.lower()
                    self.app.add_habit(name, opt)

                options = ["Daily", "Weekly", "Monthly"]
                headers = ["Interval"]
                self.submenu = Submenu(options, headers, on_confirm)

            case "r":
                # callback function to remove a certain habit
                def on_confirm(option: str):
                    if option == "yes":
                        habit = self.app.habit_at_index(self.index)
                        if not habit:
                            return
                        uid = habit.uid
                        self.app.filter.base.pop(uid)
                        self.app.filter.tmp.pop(uid)
                        self.app.save()
                        UiHelpers.draw_list(self.app, self.index)

                self.submenu = ConfirmSubmenu(on_confirm)

            case "f":
                # filter
                def on_confirm(option: str):
                    match option:
                        case "Completed":
                            self.app.filter.apply_filter("completed")
                        case "Not Completed":
                            self.app.filter.apply_filter("incomplete")
                        case "All":
                            self.app.filter.apply_filter("all")
                        case "Daily" | "Weekly" | "Monthly":
                            self.app.filter.apply_filter(option)
                    UiHelpers.draw_list(self.app, self.index)

                options = ["All", "Completed", "Not Completed", "Daily", "Weekly", "Monthly"]
                self.submenu = Submenu(options, ["Filter"], on_confirm)

            case "s":
                # sort
                def on_confirm(option: str):
                    match option:
                        case "Name ↓":
                            self.app.filter.apply_sorting("name")
                        case "Name ↑":
                            self.app.filter.apply_sorting("name_desc")
                        case "Completion ↓":
                            self.app.filter.apply_sorting("completion_desc")
                        case "Completion ↑":
                            self.app.filter.apply_sorting("completion")
                        case "Streak ↓":
                            self.app.filter.apply_sorting("longest_streak_desc")
                        case "Streak ↑":
                            self.app.filter.apply_sorting("longest_streak")
                        case "Completion Rate ↓":
                            self.app.filter.apply_sorting("comp_rate_desc")
                        case "Completion Rate ↑":
                            self.app.filter.apply_sorting("comp_rate")
                    UiHelpers.draw_list(self.app, self.index)

                options = [
                    "Name ↓",
                    "Name ↑",
                    "Completion ↓",
                    "Completion ↑",
                    "Streak ↓",
                    "Streak ↑",
                    "Completion Rate ↓",
                    "Completion Rate ↑",
                ]
                self.submenu = Submenu(options, ["Sorting"], on_confirm)

            case "I":
                UiHelpers.clear_term()
                self.app.inspect_self(False)

            case "i":
                UiHelpers.clear_term()
                self.app.inspect_self(True)

            case "CLEAR_SCREEN":
                UiHelpers.clear_term()

            case "QUIT":
                UiHelpers.clear_term()
                return True
            case "h":
                UiHelpers.clear_term()
                UiHelpers.print_help()
            case _:
                if DEBUG:
                    print(f"Key is not bound: {action}")
                pass


class UiHelpers:
    def __init__(self) -> None:
        pass

    @classmethod
    def print_help(cls):
        """
        This method prints the keybinds with their corresponding actions

        Args:
            cls (UiHelpers)

        Returns:
            None
        """
        binds = {
            # Navigation
            "k/↑": "Navigate up",
            "j/↓": "Navigate down",
            "q": "Quit",
            "ctrl-l": "Clear additional information",
            # Habit actions
            "c": "Toggle completion for this habit",
            "o": "Add new habit",
            "r": "Remove this habit",
            "i": "Inspect current filter selection",
            "I": "Display app-wide statistics",
            # Filter/Sorter
            "s": "Sort the habits",
            "f": "Filter the habits",
        }
        left_spacing = 10

        print(f"{bold_underline('Available Commands')}")
        for bind, expl in binds.items():
            print(f"{bind.ljust(left_spacing)}{expl}")

    @classmethod
    def clear_term(cls):
        """
        This method clears the terminal screen

        Args:
            cls (UiHelpers)

        Returns:
            None
        """
        os.system("cls" if os.name == "nt" else "clear")

    @classmethod
    def get_available_bytes(cls, fd: int) -> int:
        """
        This method is unix only and returns the number of bytes contained in the current stdin buffer

        Args:
            cls (UiHelpers)

        Returns:
            bytes (int): Number of bytes present in stdin
        """
        buf = array.array("i", [0])
        fcntl.ioctl(fd, termios.FIONREAD, buf)
        return buf[0]

    @classmethod
    def draw_list(cls, app: App, selected: int):
        """
        This method prints the default screen, containing the selected habits

        Args:
            cls (UiHelpers)
            app (App)
            selected (int): The index of the currently selected habit

        Returns:
        """
        options = app.filter.tmp
        spacing = 2

        def formatter(string: str) -> tuple[str, int]:
            length = len(string) + spacing
            bolded = bold(string.ljust(length))
            return (bolded, length)

        print(HIDE_CURSOR + CLEAR_SCREEN + CURSOR_HOME, end="")
        if len(options) > 0:
            max_len = max([len(item.name) for (_, item) in options.items()]) + spacing
        else:
            max_len = len("Name") + spacing

        history_tag, history_len = formatter("History")
        completed_tag, completed_len = formatter("Done")
        name_tag = bold("Name".ljust(max_len))

        print(f"  {completed_tag}{name_tag}{history_tag}")
        print("…" * (max_len + completed_len + history_len + spacing))
        options_len = len(options)
        for i, (_, item) in enumerate(options.items()):
            # Verify selected is always set, even if it's out of bounds
            if options_len <= selected:
                selected = options_len - 1
            prefix = "➤ " if i == selected else "  "

            # done = "[x]" if item.completed else "[ ]"
            # done = COMPLETED if item.completed else INCOMPLETE
            done = "☑" if item.completed else "☐"
            option = f"{done.ljust(completed_len)}{item.name.ljust(max_len)}{item.ui_history(max_rows=1)}"
            print(f"{prefix}{option}")

        # Show inspect mode
        print()
        if habit := app.habit_at_index(selected):
            habit.inspect_self()

        print(f"\n  Use ↑/↓ to navigate", flush=True)
        print(f"  Or press 'h' to show more commands", flush=True)
