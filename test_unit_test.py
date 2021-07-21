import unittest
from models.db_pantry import *


class UnitTest(unittest.TestCase):

    
    def test_pantry_db_get_items(self):
        user = 'vinh'
        table = 'test-table'
        db = DbPantry(table)

        items = db.get_items(user)
        self.assertTrue(items)
        

    def test_PantryDb_item_exist(self):
        user = 'vinh'
        ingredient = "salt"
        table = 'test-table'
        db = DbPantry(table)

        db.add_item(user, ingredient)

        item = db.get_item(user, ingredient)
        self.assertEqual(item, {'user': 'vinh', 'ingredient': 'salt'})

    def test_PantryDb_create_pantry(self):
        name = 'test-table'
        db = DbPantry(name)
        self.assertIsNotNone(db.create_pantry())
