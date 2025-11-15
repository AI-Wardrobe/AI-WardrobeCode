import pandas as pd
import unittest

from src.utils.validate_data import validate_dataframe
from src.utils.data_loader import load_tags_csv


class TestDataLoaderAndValidation(unittest.TestCase):
    def test_validate_dataframe_flags_bad_rows(self):
        # Missing filename + bad color + bad formality
        df = pd.DataFrame(
            {
                "filename": [None],
                "dominant_color": ["blue"],  # not rgb(...)
                "formality": ["very formal"],  # not int
            }
        )

        issues = validate_dataframe(df)
        self.assertGreater(len(issues), 0)
        # Just basic sanity check; don't need exact text match
        self.assertTrue(any("filename" in msg.lower() for msg in issues))

    def test_load_tags_csv_normalizes_columns(self):
        # This test assumes you will later create data/tags.csv
        # For now, just assert the function exists and raises FileNotFoundError
        try:
            load_tags_csv("data/this_file_should_not_exist.csv")
        except FileNotFoundError:
            # Expected behavior
            pass
        else:
            self.fail("Expected FileNotFoundError for missing CSV.")


if __name__ == "__main__":
    unittest.main()
