from http import HTTPStatus
from pathlib import Path
import sys
import unittest

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import (
    ApplicationTestBase,
    USER_ID2,
    app,
)


class SymbolsTest(ApplicationTestBase):
    def test_get_select_json(self):
        # GIVEN
        payload = {"q": "GOOG"}

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/select_json", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"Symbol": "GOOGL"}, response.json["symbols"][1])


if __name__ == "__main__":
    unittest.main()
