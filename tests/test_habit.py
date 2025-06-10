import unittest
from datetime import timedelta
from classes.habit import BaseHabit, DailyHabit, MonthlyHabit, WeeklyHabit
from constants import TODAY

# Run instructions:
# python -m unittest tests/habit.py


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

    def test_check_interval(self):
        """
        Tested methods:
        1. habit.check_interval
        2. habit.insert_missed
        3. habit.calculate_streaks

        This method tests the workflow for calculating missed intervals and streaks
        """

        """
        Test Case:
        Checks daily task. Last interval was completed, 19 missed afterwards
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
        Checks daily task. Last n intervals were completed. Check for current- and longest streak, and history
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
        Checks daily task. Last n intervals were completed with regular interruptions at `interrupt`.
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
        print(habit.inspect_self())

        self.assertEqual(habit.longest_streak, min(interrupt - 1, n))
        self.assertEqual(habit.current_streak, n % interrupt)
        self.assertEqual(habit.longest_negative, 1)

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
