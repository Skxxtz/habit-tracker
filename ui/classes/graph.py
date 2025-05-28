from classes.habit import BaseHabit
from helpers.text import bold_underline


class Graph:
    habits: dict[str, BaseHabit]
    padding: int
    max_items: int

    def __init__(self, habits: dict[str, BaseHabit]) -> None:
        self.habits = habits
        self.max_items = 20
        self.padding = 2
        self.draw()

    def draw(self) -> None:
        habits = self.habits.values()
        # Header
        print(f"{bold_underline('Habit Completions')}", end="\n\n")

        # Get maximum and minimum number of completions
        completion_counts = [sum(item.history) for item in habits]
        max_compl = max(completion_counts)
        maximum = min(max_compl, self.max_items)
        minimum = min(completion_counts)
        offset = minimum - 1

        # construct graph lines for each habit
        for habit, completed in zip(habits, completion_counts):
            visible = min(maximum, completed)
            bars = visible - offset
            empty = maximum - bars

            points = "⣿" * bars
            padding = " " * empty
            habit_padding = " " * self.padding
            num_completed = (
                " " * len(str(maximum)) if visible == completed else f"{completed}"
            )
            print(f"{points}{padding}{num_completed}{habit_padding}{habit.name}")

        # Axis line
        left = str(offset + 1)
        right = str(maximum)
        if (spacing:=(maximum - offset - len(left) - len(right))) <= 0:
            print(right)
        else:
            axis_padding = " " * spacing
            print(f"{left}{axis_padding}{right}")
