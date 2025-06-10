from typing import Optional
from classes.habit import BaseHabit

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
    def apply_sorting(self, sorter: Optional[str] = None):
        sorter = sorter or self.sorter
        match sorter:
            case "name":
                self._sort_by_name()
            case "name_desc":
                self._sort_by_name(True)
            case "completion":
                self._sort_by_completion()
            case "completion_desc":
                self._sort_by_completion(True)
            case "longest_streak":
                self._sort_by_streak()
            case "longest_streak_desc":
                self._sort_by_streak(True)
            case "comp_rate":
                self._sort_by_comp_rate()
            case "comp_rate_desc":
                self._sort_by_comp_rate(True)
            case _:
                return

        self.sorter = sorter

    def _sort_by_name(self, rev: bool = False, inplace: bool = True)->Optional[dict[str, BaseHabit]]:
        tmp = dict(sorted(self.tmp.items(), key=lambda item: item[1].name, reverse=rev))
        if inplace:
            self.tmp = tmp
        else:
            return tmp

    def _sort_by_completion(self, rev: bool = False, inplace: bool = True)->Optional[dict[str, BaseHabit]]:
        tmp = dict(sorted(self.tmp.items(), key=lambda item: item[1].completed, reverse=rev))
        if inplace:
            self.tmp = tmp
        else:
            return tmp
    def _sort_by_comp_rate(self, rev: bool = False, inplace: bool = True)->Optional[dict[str, BaseHabit]]:
        tmp = dict(sorted(self.tmp.items(), key=lambda item: (sum(item[1].history) / len(item[1].history)), reverse=rev))
        if inplace:
            self.tmp = tmp
        else:
            return tmp
    def _sort_by_streak(self, rev: bool = False, inplace: bool = True)->Optional[dict[str, BaseHabit]]:
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
                self._filter_completed(True)
            case "incomplete":
                self._filter_completed(False)

            case "daily" | "weekly" | "monthly":
                self._filter_interval(filter)
            case _: 
                return

        self.filter = filter

    def _filter_completed(self, completed: bool = False):
        self.tmp = {k: v for k, v in self.base.items() if v.completed == completed}

    def _filter_interval(self, interval: str):
        self.tmp = {k: v for k, v in self.base.items() if v.interval == interval}
