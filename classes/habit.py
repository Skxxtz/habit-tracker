from datetime import datetime, timedelta
from typing import Any, List
from abc import ABC, abstractmethod
import uuid

from constants import DEBUG, DATEFORMAT, TODAY
from helpers.text import green, percentage_gradient, red, underline


class BaseHabit(ABC):
    # Attributes
    name: str
    uid: str
    completed: int
    longest_streak: int
    longest_negative: int
    current_negative: int
    current_streak: int
    interval: str
    start: datetime
    history: List[int]

    # Formatting
    num_intervals: int

    def __init__(self, name: str, interval: str) -> None:
        self.name = name
        self.uid = str(uuid.uuid4())
        self.interval = interval

        self.longest_streak = 0
        self.current_streak = 0
        self.longest_negative = 1
        self.current_negative = 1
        self.history = []

        self.reset()

    @classmethod
    def create(cls, name: str, interval: str) -> "BaseHabit":
        match interval:
            case "monthly":
                habit = MonthlyHabit(name)
            case "weekly":
                habit = WeeklyHabit(name)
            case _:
                habit = DailyHabit(name)

        return habit

    def __str__(self) -> str:
        return (
            f"Habit: {self.name}\n"
            f"Interval: {self.interval}\n"
            f"completed: {self.completed}\n"
            f"Current Streak: {self.current_streak}\n"
            f"Longest Streak: {self.longest_streak}"
        )

    def __eq__(self, value: object) -> bool:
        """
        This method is used to compare two Habit instances for equality

        Args:
            self (Habit)
            value (object): The object `self` is compared to

        Returns:
            None
        """
        if not isinstance(value, BaseHabit):
            return False

        if self.name != value.name:
            if DEBUG:
                print("Names don't match")
            return False

        if self.longest_negative != value.longest_negative:
            if DEBUG:
                print("Longest negative values don't match")
            return False

        if self.current_negative != value.current_negative:
            if DEBUG:
                print("Current negative values don't match")
            return False

        if self.longest_streak != value.longest_streak:
            if DEBUG:
                print("Longest streaks don't match")
            return False

        if self.current_streak != value.current_streak:
            if DEBUG:
                print("Current streaks don't match")
            return False

        if self.start.date() != value.start.date():
            if DEBUG:
                print("Start dates don't match")
            return False

        if self.history != value.history:
            if DEBUG:
                print("Histories don't match")
            return False

        return True

    @abstractmethod
    def reset(self):
        pass

    def inspect_self(self, prefix: str = "  ") -> None:
        """
        This method displays analytical information about the habit at index i. This inculdes statistics such as longest streak, and completion history

        Args:
            self (Habit)

        Returns:
            None
        """
        # get the history in an understandable way
        history_len = len(self.history)
        ones = sum(self.history)
        zeros = history_len - ones

        # show the last 10 results nicely formatted
        print(f"{prefix}{underline(self.name)}")
        print(f"{prefix}{self.ui_history(prefix)}")
        print(f"{prefix}Interval: {self.interval.title()}")
        print(f"{prefix}Completed: {ones}/{history_len}")
        print(f"{prefix}Incomplete: {zeros}/{history_len}")
        print(f"{prefix}Longest Streak: {self.longest_streak}")
        print(f"{prefix}Current Streak: {self.current_streak}")
        print(f"{prefix}Longest Negative Streak: {self.longest_negative}")
        print(f"{prefix}Current Negative Streak: {self.current_negative}")
        comp_rate = ones / history_len * 100
        print(f"{prefix}Completion Rate: {percentage_gradient(comp_rate)}")

    def insert_missed(self, missed: int):
        """
        This method either updates the current streak or inserts

        Args:
            self (Habit)
            missed (int): The number of missed intervals. i.e. With "weekly" n missed are n weeks

        Returns:
            None
        """
        self.current_streak += self.completed
        self.current_negative -= self.completed - 1

        if self.current_streak > self.longest_streak:
            self.longest_streak = self.current_streak

        # update
        self.current_negative += max(missed, 0)
        if self.current_negative > self.longest_negative:
            self.longest_negative = self.current_negative

        if not self.completed or missed > 1:
            self.current_streak = 0
        else:
            self.current_negative = 0

        for _ in range(missed - 1):
            self.history.append(0)

        self.reset()

    @abstractmethod
    def check_interval(self) -> tuple[int, int]:
        """
        This function checks first checks if the current date is out of bounds of the desired interval.
        For example: For daily habits, it checks whether the date has changed. For monthly habits, it checks whether the month or year have changed.
        Then the habit state gets resetted.

        Args:
            self (Habit)

        Returns:
            (current streak, current negative)((int, int)): Returns the current negative and positive streaks

        """
        pass

    def toggle_completed(self) -> None:
        """
        This method toggles the completion of this habit. It also handles updating the history and calls the update function for the streaks.

        Args:
            self (Habit)

        Returns:
            None
        """
        self.completed = 0 if self.completed else 1
        self.history[-1] = self.completed
        self.calculate_streaks()

    def calculate_streaks(self) -> None:
        """
        This method calculates and updates the (1) current positive, (2) current negative, (3) longest positive, and (4) longest negative streak.

        Args:
            self (Habit)

        Returns:
            None
        """
        longest_positive = longest_negative = 0
        current_positive = current_negative = 0

        for value in self.history:
            if value:
                current_positive += 1
                longest_negative = max(longest_negative, current_negative)
                current_negative = 0
            else:
                current_negative += 1
                longest_positive = max(longest_positive, current_positive)
                current_positive = 0

        # Final check in case the list ends with a streak
        longest_positive = max(longest_positive, current_positive)
        longest_negative = max(longest_negative, current_negative)

        self.current_streak = current_positive
        self.current_negative = current_negative
        self.longest_streak = longest_positive
        self.longest_negative = longest_negative

    def ui_history(self, prefix: str = "", max_rows: int = 3) -> str:
        """
        This method formats the completion history.

        Args:
            self (Habit)
            prefix (str): The string that should be prefixed on every line
            max_rows (int) = 3: The maxmimum number of rows displayed

        Returns:
            string (str): The formated string
        """
        num_intervals = self.num_intervals or 7

        colored = [green("■") if i == 1 else red("■") for i in self.history[::-1]]
        upper_bound = min(max_rows * num_intervals, len(self.history))
        lines = [
            "".join(colored[i : i + num_intervals])
            for i in range(0, upper_bound, num_intervals)
        ]
        return f"\n{prefix}".join(lines)

    def to_dict(self) -> dict[str, Any]:
        """
        This method serializes the Habit instance into a dict for json dumping

        Args:
            self (Habit)

        Returns:
            habit (dict): A HashMap containing the attributes of the current instance
        """
        data = {}
        data["uid"] = self.uid
        data["name"] = self.name
        data["interval"] = self.interval
        data["completed"] = self.completed
        data["start"] = datetime.strftime(self.start, DATEFORMAT)

        data["longest_streak"] = self.longest_streak
        data["current_streak"] = self.current_streak
        data["longest_negative"] = self.longest_negative
        data["current_negative"] = self.current_negative
        data["history"] = self.history
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseHabit":
        """
        This method deserializes a Habit instance from a HashMap

        Args:
            cls (Habit)
            data (dict): HashMaps containing the needed data for deserialization

        Returns:
            habit (Habit): A Habit instance deserialized from the dict
        """
        habit = BaseHabit.create(data["name"], data["interval"])
        habit.uid = data["uid"]
        habit.completed = data["completed"]
        habit.start = datetime.strptime(data["start"], DATEFORMAT)

        habit.longest_streak = data["longest_streak"]
        habit.current_streak = data["current_streak"]
        habit.longest_negative = data["longest_negative"]
        habit.current_negative = data["current_negative"]
        habit.history = data["history"]

        # update with current data
        habit.check_interval()
        return habit


# SUBCLASSES
class DailyHabit(BaseHabit):
    def __init__(self, name: str) -> None:
        self.num_intervals = 7
        super().__init__(name, "daily")

    def reset(self):
        self.start = TODAY
        self.completed = 0
        self.history.append(0)

    def check_interval(self) -> tuple[int, int]:
        if self.start.date() != TODAY.date():
            missed = (TODAY - self.start).days
            self.insert_missed(missed)
        return (self.current_streak, self.current_negative)


class WeeklyHabit(BaseHabit):
    def __init__(self, name: str) -> None:
        self.num_intervals = 4
        super().__init__(name, "weekly")

    def check_interval(self) -> tuple[int, int]:
        this_week = TODAY - timedelta(days=TODAY.weekday())
        if self.start.date() != this_week.date():
            missed = (this_week - self.start).days // 7
            self.insert_missed(missed)
        return (self.current_streak, self.current_negative)

    def reset(self):
        self.start = TODAY - timedelta(days=TODAY.weekday())
        self.completed = 0
        self.history.append(0)


class MonthlyHabit(BaseHabit):
    def __init__(self, name: str) -> None:
        self.num_intervals = 5
        super().__init__(name, "monthly")

    def reset(self):
        self.start = TODAY.replace(day=1)
        self.completed = 0
        self.history.append(0)

    def check_interval(self) -> tuple[int, int]:
        if (self.start.month, self.start.year) != (TODAY.month, TODAY.year):
            missed = (
                (TODAY.year - self.start.year) * 12 + TODAY.month - self.start.month
            )
            self.insert_missed(missed)
        return (self.current_streak, self.current_negative)
