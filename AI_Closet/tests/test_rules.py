
import unittest
from src.recommender.rules import Item, recommend

class TestRules(unittest.TestCase):
    def test_recommend_minimal(self):
        items = [
            Item(1, "top", "rgb(200,200,200)"),
            Item(2, "bottom", "rgb(30,30,30)"),
        ]
        ctx = {"temp_f": 65}
        recs = recommend(items, ctx)
        self.assertTrue(len(recs) >= 1)

if __name__ == "__main__":
    unittest.main()
