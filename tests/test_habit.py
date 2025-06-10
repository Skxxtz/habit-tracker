import unittest
from datetime import timedelta
from classes.habit import BaseHabit, DailyHabit, MonthlyHabit, WeeklyHabit
from constants import TODAY

# Run instructions:
# python -m unittest tests/test_habit.py


"""
This file includes tests for the BaseHabit class.

Tested?
# BaseHabit
[x] reset (abstract, implemented in subclasses)  
[x] check_interval (abstract, implemented in subclasses)

[-] __init__            # not planned
[x] create
[x] __str__
[x] __eq__
[-] inspect_self        # not planned
[x] insert_missed
[x] toggle_completed
[x] calculate_streaks
[-] ui_history          # not planned
[x] to_dict
[x] from_dict

# DailyHabit

[-] __init__            # not planned
[x] reset
[x] check_interval

# WeeklyHabit

[-] __init__            # not planned
[x] check_interval
[x] reset

# MonthlyHabit

[-] __init__            # not planned
[x] reset
[x] check_interval


"""


class TestHabit(unittest.TestCase):
    def test_eq(self):
        """
        Tested methods:
        1. habit.__eq__
        """
        habit = BaseHabit.create("Test Habit", "monthly")
        habit1 = BaseHabit.create("Test Habit", "monthly")

        self.assertEqual(habit, habit1)

    def test_create(self):
        """
        Tested methods:
        1. habit.toggle_completed 
        """

        """
        Test Case:
        Tests creation for daily habits
        """ 

        habit = BaseHabit.create("Test Habit", "daily")
        should_be = DailyHabit("Test Habit")
        self.assertEqual(habit, should_be)

        """
        Test Case:
        Tests creation for weekly habits
        """
        habit = BaseHabit.create("Test Habit", "weekly")
        should_be = WeeklyHabit("Test Habit")
        self.assertEqual(habit, should_be)

        """
        Test Case:
        Tests creation for monthly habits
        """
        habit = BaseHabit.create("Test Habit", "monthly")
        should_be = MonthlyHabit("Test Habit")
        self.assertEqual(habit, should_be)
        
    def test_toggle_completed(self):
        """
        Tested methods:
        1. habit.toggle_completed 
        """
        habit = BaseHabit.create("Test Habit", "monthly")
        self.assertEqual(habit.completed, 0)
        self.assertEqual(habit.history[-1], 0)
        habit.toggle_completed()
        self.assertEqual(habit.completed, 1)
        self.assertEqual(habit.history[-1], 1)

    def test_check_interval_daily(self):
        """
        Tested methods:
        1. DailyHabit.check_interval
        2. BaseHabit.insert_missed
        3. BaseHabit.calculate_streaks
        4. DailyHabit.reset

        This method tests the workflow for calculating missed intervals and streaks
        """

        """
        Test Case:
        Last interval was completed, 19 missed afterwards
        """
        habit = BaseHabit.create("Test Habit", "daily")
        habit.toggle_completed()
        habit.start = TODAY - timedelta(days=20)

        habit.check_interval()
        habit.calculate_streaks()

        should_be = [0 for _ in range(20)]
        self.assertEqual(habit.history, [1] + should_be)
        self.assertEqual(habit.longest_streak, 1)
        self.assertEqual(habit.current_streak, 0)
        self.assertEqual(habit.current_negative, 20)
        self.assertEqual(habit.longest_negative, 20)

        """
        Test Case:
        Last n intervals were completed
        """
        yesterday = TODAY - timedelta(days=1)
        n = 5
        should_be = [1 for _ in range(n)]

        habit = BaseHabit.create("Test Habit", "daily")
        for _ in range(n - 1):
            habit.toggle_completed()
            habit.start = yesterday
            habit.check_interval()
        habit.toggle_completed()

        self.assertEqual(habit.history, should_be)
        self.assertEqual(habit.current_streak, n)
        self.assertEqual(habit.longest_streak, n)

        """
        Test Case:
        Last n intervals were completed with regular interruptions at `interrupt`
        """
        yesterday = TODAY - timedelta(days=1)
        n = 100
        interrupt = 20
        should_be = [1 for _ in range(n)]

        habit = BaseHabit.create("Test Habit", "daily")
        for i in range(n):
            habit.start = yesterday
            habit.check_interval()
            if (i+1) % interrupt != 0:
                habit.toggle_completed()
        habit.calculate_streaks()

        self.assertEqual(habit.longest_streak, min(interrupt - 1, n))
        self.assertEqual(habit.current_streak, n % interrupt)
        self.assertEqual(habit.longest_negative, 1)

    def test_check_interval_weekly(self):
        """
        Tested methods:
        1. WeeklyHabit.check_interval
        2. WeeklyHabit.reset

        This method tests the workflow for calculating missed intervals and streaks
        """

        """
        Test Case:
        First interval was completed, 19 missed days after
        """
        habit = BaseHabit.create("Test Habit", "weekly")
        habit.toggle_completed()
        intermediate = TODAY - timedelta(days=20) # set time 20 days to past
        habit.start = intermediate - timedelta(days=intermediate.weekday()) # set date to monday of that week

        missed = (TODAY - habit.start).days // 7 # is always 1 more, since current interval is accounted for
        habit.check_interval()
        habit.calculate_streaks()

        should_be = [0 for _ in range(missed)]
        self.assertEqual(habit.history, [1] + should_be)
        self.assertEqual(habit.longest_streak, 1)
        self.assertEqual(habit.current_streak, 0)
        self.assertEqual(habit.current_negative, missed)
        self.assertEqual(habit.longest_negative, missed) 

        """
        Test Case:
        Last n intervals were completed
        """
        intermediate = TODAY - timedelta(days=TODAY.weekday() + 7) # set to last week monday
        n = 5
        should_be = [1 for _ in range(n)]

        habit = BaseHabit.create("Test Habit", "weekly")
        for _ in range(n - 1):
            habit.toggle_completed()
            habit.start = intermediate
            habit.check_interval()
        habit.toggle_completed()

        self.assertEqual(habit.history, should_be)
        self.assertEqual(habit.current_streak, n)
        self.assertEqual(habit.longest_streak, n)

        """
        Test Case:
        Last n intervals were completed with regular interruptions at `interrupt`
        """
        yesterday = TODAY - timedelta(days=TODAY.weekday() + 7)
        n = 100
        interrupt = 20
        should_be = [1 for _ in range(n)]

        habit = BaseHabit.create("Test Habit", "weekly")
        for i in range(n):
            habit.start = yesterday
            habit.check_interval()
            if (i+1) % interrupt != 0:
                habit.toggle_completed()
        habit.calculate_streaks()

        self.assertEqual(habit.longest_streak, min(interrupt - 1, n))
        self.assertEqual(habit.current_streak, n % interrupt)
        self.assertEqual(habit.longest_negative, 1)

    def test_check_interval_monthly(self):
        """
        Tested methods:
        1. MonthlyHabit.check_interval
        2. MonthlyHabit.reset # by extension within insert_missed

        This method tests the workflow for calculating missed intervals and streaks
        """

        """
        Test Case:
        First interval was completed, only missed afterwards (with year break)
        """
        habit = BaseHabit.create("Test Habit", "monthly")
        habit.toggle_completed()
        intermediate = TODAY - timedelta(days=400) # set time 120 days to past
        habit.start = intermediate.replace(day=1) # set date to first of month


        if (habit.start.month, habit.start.year) != (TODAY.month, TODAY.year):
            missed = (
                (TODAY.year - habit.start.year) * 12 + TODAY.month - habit.start.month
            )

            habit.check_interval()
            habit.calculate_streaks()

            should_be = [0 for _ in range(missed)]
            self.assertEqual(habit.history, [1] + should_be)
            self.assertEqual(habit.longest_streak, 1)
            self.assertEqual(habit.current_streak, 0)
            self.assertEqual(habit.current_negative, missed)
            self.assertEqual(habit.longest_negative, missed) 

        """
        Test Case:
        Last n intervals were completed
        """
        intermediate = TODAY.replace(day=1, month=TODAY.month - 1) # set to last month
        n = 5
        should_be = [1 for _ in range(n)]

        habit = BaseHabit.create("Test Habit", "monthly")
        for _ in range(n - 1):
            habit.toggle_completed()
            habit.start = intermediate
            habit.check_interval()
        habit.toggle_completed()

        self.assertEqual(habit.history, should_be)
        self.assertEqual(habit.current_streak, n)
        self.assertEqual(habit.longest_streak, n)

        """
        Test Case:
        Last n intervals were completed with regular interruptions at `interrupt`
        """
        yesterday = TODAY.replace(day=1, month=TODAY.month - 1) # first of last month
        n = 100
        interrupt = 20
        should_be = [1 for _ in range(n)]

        habit = BaseHabit.create("Test Habit", "monthly")
        for i in range(n):
            habit.start = yesterday
            habit.check_interval()
            if (i+1) % interrupt != 0:
                habit.toggle_completed()
        habit.calculate_streaks()

        self.assertEqual(habit.longest_streak, min(interrupt - 1, n))
        self.assertEqual(habit.current_streak, n % interrupt)
        self.assertEqual(habit.longest_negative, 1)

    def test_str(self):
        """
        Tested methods:
        1. BaseHabit.__str__
        """
        habit = BaseHabit.create("Test Habit", "daily")
        string = str(habit)
        should_be = f"Habit: {habit.name}\nInterval: {habit.interval}\nCompleted: {habit.completed}\nCurrent Streak: {habit.current_streak}\nLongest Streak: {habit.longest_streak}"
        self.assertEqual(string, should_be)

    def test_serialization(self):
        """
        Tested methods:
        1. habit.from_dict
        2. habit.to_dict
        """

        """
        Test Case:
        Tests serialization and deserialization
        """
        habit = BaseHabit.create("Test Habit", "daily")
        serialized = habit.to_dict()
        deserialized = BaseHabit.from_dict(serialized)
        self.assertEqual(habit, deserialized)


if __name__ == "__main__":
    unittest.main()
