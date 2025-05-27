import unittest
from datetime import timedelta
from classes.habit import BaseHabit
from constants import TODAY

# Run instructions:
# python -m unittest tests/habit.py


class TestHabit(unittest.TestCase):
    def test_check_interval(self):
        """
        Test Case:
        Checks daily task. Last interval was completed, 19 missed afterwards
        """
        habit = BaseHabit.create("Test Habit", "daily")
        habit.toggle_completed()
        habit.start = TODAY - timedelta(days=20)

        habit.check_interval()
        habit.calculate_streaks()

        should_be = [0 for _ in range(19)]
        self.assertEqual(habit.history, [1] + should_be)
        self.assertEqual(habit.longest_streak, 1)
        self.assertEqual(habit.current_streak, 0)
        self.assertEqual(habit.current_negative, 19)
        self.assertEqual(habit.longest_negative, 19)

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
        n = 50
        interrupt = 25
        should_be = [1 for _ in range(n)]

        habit = BaseHabit.create("Test Habit", "daily")
        for i in range(n):
            habit.completed = 1 if (i + 1) % interrupt != 0 else 0
            habit.start = yesterday
            habit.check_interval()
        self.assertEqual(habit.longest_streak, min(interrupt - 1, n))
        self.assertEqual(habit.current_streak, n % interrupt)
        self.assertEqual(habit.longest_negative, 1)

    def test_serialization(self):
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
