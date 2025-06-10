import sys
from typing import Optional
import json

from classes.habit import BaseHabit
from classes.filter import Filter
from helpers.text import underline, bold
from ui.classes.graph import Graph


class App:
    filter: Filter
    longest_streak: Optional[str]
    longest_negative: Optional[str]
    save_path: str
    def __init__(self) -> None:
        self.filter = Filter({})
        self.longest_streak = None
        self.longest_negative = None

    def save(self)->None:
        data = {}
        data["habits"] = {k: v.to_dict() for k, v in self.filter.base.items()}
        data["longest_streak"] = self.longest_streak or None

        with open(self.save_path, "w+") as file:
            json.dump(data, file)

    def add_habit(self, name: str, interval: str)->None:
        habit = BaseHabit.create(name, interval)
        self.filter.base[habit.uid] = habit
        self.filter.apply_filter()
        self.save()

    def habit_at_index(self, index: int)->Optional[BaseHabit]:
        # early return if index is out of range
        filter_len = len(self.filter.tmp) 
        if filter_len <= index or filter_len == 0:
            return None
        return list(self.filter.tmp.items())[index][1]

    def display_habits(self)->None:
        spacing = 4
        def formatter(string: str)->tuple[str, int]:
            length = len(string) + spacing
            bolded = bold(string.ljust(length))
            return (bolded, length)
        
        max_len = max([len(item.name) for (_, item) in self.filter.tmp.items()]) + spacing
        
        index_tag, index_len = formatter("Index")
        history_tag, history_len = formatter("History")
        completed_tag, completed_len = formatter("History")
        name_tag = bold("Name".ljust(max_len))

        completed_left = completed_len // 2
        completed_right = completed_len - completed_left

        print(f"{index_tag}{completed_tag}{name_tag}{history_tag}")
        print("…" * (max_len + index_len + completed_len + history_len))
        for i, (_, item) in enumerate(self.filter.tmp.items()):
            
            done = "[x]" if item.completed else "[ ]" 
            done = done.rjust(completed_left) + " " * completed_right
            index = f"{i:02d}".ljust(index_len)
            print(f"{index}{done}{item.name.ljust(max_len)}{item.ui_history(max_rows = 10)}")

    def inspect_self(self, use_filter: bool)->None:
        '''
        This method displays analytical information about all habits.

        Args:
            self (App)

        Returns:
            None
        '''
        values = self.filter.tmp if use_filter else self.filter.base

        if len(values) == 0:
            return

        current_streak = max(values.values(), key=lambda obj: obj.current_streak)
        longest_streak = max(values.values(), key=lambda obj: obj.longest_streak)
        current_negative = max(values.values(), key=lambda obj: obj.current_negative)
        longest_negative = max(values.values(), key=lambda obj: obj.longest_negative)


        print()
        if current_streak.current_streak > 0:
            print(f"{underline('Currently Best Streak')}")
            print(current_streak.name)
            print(f"Current Streak: {current_streak.current_streak}", end="\n\n")

        if longest_streak.longest_streak > 0:
            print(f"{underline('Longest Streak Overall')}")
            print(longest_streak.name)
            print(f"Longest Streak: {longest_streak.longest_streak}", end="\n\n")

        if current_negative.current_negative > 0:
            print(f"{underline('Currently Worst Streak')}")
            print(current_negative.name)
            print(f"Current Negative: {current_negative.current_negative}", end="\n\n")

        if longest_negative.longest_negative > 0:
            print(f"{underline('Worst Streak Overall')}")
            print(longest_negative.name)
            print(f"Longest Negative: {longest_negative.longest_negative}", end="\n\n")

        Graph(values)

    @classmethod
    def get_or_init(cls, path) -> "App":
        '''
        This method initializes an app either using provied savedata or from scratch
        '''
        app = cls()
        app.save_path = path
        try:
            with open(app.save_path, "r") as file:
                data = json.load(file)
                app.filter.populate({k: BaseHabit.from_dict(v) for k, v in data.get("habits", {}).items()})
                longest_overall = max(app.filter.base.items(), key=lambda item: item[1].longest_streak)
                app.longest_streak = app.longest_streak or longest_overall[0]
                if streak := app.filter.base.get(app.longest_streak, longest_overall[1]):
                    if streak != longest_overall[1] and longest_overall[1].longest_streak > streak.longest_streak:
                        cls.longest_streak = longest_overall[0]

                longest_overall_neg = max(app.filter.base.items(), key=lambda item: item[1].longest_negative)
                app.longest_negative = app.longest_negative or longest_overall_neg[0]
                if streak := app.filter.base.get(app.longest_negative, longest_overall_neg[1]):
                    if streak != longest_overall_neg[1] and longest_overall_neg[1].longest_negative > streak.longest_negative:
                        cls.longest_streak = longest_overall[0]
                    
                app.filter.apply_sorting()

        except FileNotFoundError:
            # we just init a new app if no savedata is found
            pass
        except json.JSONDecodeError:
            print("Save data could not be parsed")
            sys.exit(1)
        return app
