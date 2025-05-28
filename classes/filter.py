from typing import Optional
from classes.habit import BaseHabit
from helpers.log import log


class Filter:
    base: dict[str, BaseHabit]
    tmp: dict[str, BaseHabit]
    sorter: str
    filter: str
    def __init__(self, habits: dict[str, BaseHabit]) -> None:
        self.base = habits
        self.tmp = habits
        self.sorter = "name"
        self.filter = "all"

    def populate(self, habits: dict[str, BaseHabit])->None:
        self.base = habits
        self.tmp = habits

    # SORTERS
    def apply_sorting(self, key: Optional[str] = None):
        key = key or self.sorter
        match key:
            case "name":
                self.sort_by_name()
            case "name_desc":
                self.sort_by_name(True)
            case "completion":
                self.sort_by_completion()
            case "completion_desc":
                self.sort_by_completion(True)
            case _:
                return

        self.sorter = key

    def sort_by_name(self, rev: bool = False, inplace: bool = True)->Optional[dict[str, BaseHabit]]:
        tmp = dict(sorted(self.tmp.items(), key=lambda item: item[1].name, reverse=rev))
        if inplace:
            self.tmp = tmp
        else:
            return tmp

    def sort_by_completion(self, rev: bool = False, inplace: bool = True)->Optional[dict[str, BaseHabit]]:
        tmp = dict(sorted(self.tmp.items(), key=lambda item: item[1].completed, reverse=rev))
        if inplace:
            self.tmp = tmp
        else:
            return tmp
    def sort_by_streak(self, rev: bool = False, inplace: bool = True)->Optional[dict[str, BaseHabit]]:
        tmp = dict(sorted(self.tmp.items(), key=lambda item: item[1].longest_streak, reverse=rev))
        if inplace:
            self.tmp = tmp
        else:
            return tmp

    # FILTERS
    def apply_filter(self, filter: Optional[str] = None):
        filter = filter or self.filter
        filter = filter.lower()
        match filter:
            case "all":
                self.tmp = self.base
            case "completed":
                self.filter_completed(True)
            case "incomplete":
                self.filter_completed(False)

            case "daily" | "weekly" | "monthly":
                self.filter_interval(filter)
            case _: 
                return

        self.filter = filter
        self.apply_sorting()

    def filter_completed(self, completed: bool = False):
        self.tmp = {k: v for k, v in self.base.items() if v.completed == completed}

    def filter_interval(self, interval: str):
        self.tmp = {k: v for k, v in self.base.items() if v.interval == interval}
