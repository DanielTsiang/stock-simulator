from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
import sys
import unittest

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import (
    ApplicationTestBase,
    HISTORY_ID,
    PRICE,
    SYMBOL,
    USER_ID1,
    USER_ID2,
    app,
    captured_templates,
    db,
)

import utils


class HistoryTest(ApplicationTestBase):
    def test_get_history(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # Mock user logged in
                with test_client.session_transaction() as session:
                    session["user_id"] = USER_ID2
                # WHEN
                response = test_client.get("/history")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("history.html", template.name)

    def test_delete_history(self):
        # GIVEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID1
            # WHEN
            response = test_client.delete("/history")

        # Obtain history information for logged-in user
        transactions = db.execute(
            "SELECT * FROM history WHERE user_id = ? ORDER BY transacted DESC", USER_ID1
        )

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)
        self.assertEqual([], transactions)

    def test_get_history_json(self):
        # GIVEN
        expected_history = {
            "data": [
                {
                    "id": HISTORY_ID,
                    "price": utils.usd(PRICE),
                    "shares": 1,
                    "symbol": SYMBOL,
                    "transacted": None,
                    "user_id": USER_ID2,
                }
            ]
        }

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/history_json")
            expected_history["data"][0]["transacted"] = datetime.now(timezone.utc).strftime(
                                                            "%d-%m-%Y %H:%M:%S"
                                                        )

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected_history, response.json)


if __name__ == "__main__":
    unittest.main()
