import os
import unittest

from scripts.validate_marketplace import validate_marketplace


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class TestMarketplace(unittest.TestCase):
    def test_marketplace_matches_skills_repository(self):
        result = validate_marketplace(REPO_ROOT)
        self.assertTrue(
            result["ok"],
            "marketplace validation failed:\n" + "\n".join(result["errors"]),
        )


if __name__ == "__main__":
    unittest.main()
