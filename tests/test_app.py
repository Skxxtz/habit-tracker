import json
from os import remove
import unittest
from classes.application import App
from classes.habit import BaseHabit

# Run instructions:
# python -m unittest tests/test_app.py

"""
This file includes tests for the App class.

Tested?
# App
[-] __init__            # trivial, not planned  
[-] display_habits      # ui effect, not planned
[-] inspect_self        # ui component, not planned 
[ ] get_or_init
[ ] save  
[ ] add_habit  
[ ] habit_at_index  
"""


class TestApp(unittest.TestCase):
    def test_get_or_init(self):
        """
        Tested methods:
        1. App.get_or_init
        """
        save_path = "tests.json.tmp"
        habit = BaseHabit.create("Example Habit 1", "weekly")
        habit2 = BaseHabit.create("Exa 2", "monthly")
        habits = [habit, habit2]
        data = {}

        data["habits"] = {v.uid: v.to_dict() for v in habits}
        data["longest_streak"] = None
        with open(save_path, "w+") as f:
            json.dump(data, f)

        app = App.get_or_init(save_path)
        for (a, b) in zip(app.filter.base.values(), habits):
            self.assertEqual(a, b)

        remove(app.save_path)
    
    def test_save(self):
        """
        Tested methods:
        1. App.save
        2. App.add_habit
        """
        app = App()
        app.save_path = "tests.json.tmp"
        app.add_habit("Example Habit1", "weekly")
        app.add_habit("Example Habit2", "monthly")

        self.assertEqual(len(app.filter.base.values()), 2) # check if habits were inserted
        app.save()

        app2 = App.get_or_init(app.save_path)
        self.assertEqual(len(app2.filter.base.values()), 2) # check if habits were loaded

        # check if the items are the same
        for (a, b) in zip(app.filter.base.values(), app2.filter.base.values()):
            self.assertEqual(a, b)

        # remove file
        remove(app.save_path)
        

    def test_habit_at_index(self):
        """
        Tested methods:
        1. App.habit_at_index
        2. Filter.apply_filter # by extension
        3. Filter.apply_sorter # by extension
        """
        app = App()
        app.save_path = "tests.json.tmp"
        app.add_habit("Example Habit1", "weekly")
        app.add_habit("A Habit", "monthly")

            
        first = app.habit_at_index(0)
        self.assertIsNot(first, None) # ensure index exists
        if first:
            self.assertEqual(first.name, "A Habit") # if true, sorting works too

        app.filter.apply_sorting("name_desc")
    
        first = app.habit_at_index(0)
        self.assertIsNot(first, None) # ensure index exists
        if first:
            self.assertEqual(first.name, "Example Habit1") # if true, sorting works too

    
if __name__ == "__main__":
    unittest.main()
