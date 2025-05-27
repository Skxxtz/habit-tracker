from typing import Callable, Optional

from constants import CLEAR_SCREEN, CURSOR_HOME, HIDE_CURSOR
from helpers.text import bold


class Submenu:
    def __init__(
        self,
        options: list[str],
        headers: list[str],
        on_confirm: Optional[Callable[[str], None]] = None,
    ) -> None:
        self.options = options
        self.headers = headers
        self.on_confirm = on_confirm
        self.index = 0
        self.refresh()

    def up(self):
        self.index = (self.index - 1) % len(self.options)

    def down(self):
        self.index = (self.index + 1) % len(self.options)

    def refresh(self):
        print(HIDE_CURSOR + CLEAR_SCREEN + CURSOR_HOME, end="")

        def formatter(string: str) -> tuple[str, int]:
            length = len(string) + spacing
            bolded = bold(string.ljust(length))
            return (bolded, length)

        spacing = 2

        headers = dict([formatter(head) for head in self.headers])
        header = f"  {' '.join(headers.keys())}"
        print(header)
        print("…" * len(header))

        for i, item in enumerate(self.options):
            prefix = "➤ " if i == self.index else "  "
            option = f"{item}"
            print(f"{prefix}{option}")
        print("\nUse ↑/↓ and press Enter", flush=True)

    def activate(self):
        option = self.options[self.index]
        if self.on_confirm:
            self.on_confirm(option)


class ConfirmSubmenu(Submenu):
    def __init__(self, on_confirm: Optional[Callable[[str], None]] = None) -> None:
        self.options = ["yes", "no"]
        self.headers = ["Confirm?"]
        self.on_confirm = on_confirm
        super().__init__(self.options, self.headers, on_confirm)
