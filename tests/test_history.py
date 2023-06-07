import sys
import unittest
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path
from unittest import mock

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

import utils
from tests.application_test_base import (
    HISTORY_ID,
    PRICE,
    SYMBOL,
    USER_ID1,
    USER_ID2,
    ApplicationTestBase,
    app,
    captured_templates,
    db,
)


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

    @mock.patch("routes.history.datetimeformat")
    def test_get_history_json(self, mock_datetime):
        # GIVEN
        transaction_timestamp = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")
        mock_datetime.return_value = transaction_timestamp
        expected_results = {
            "data": [
                {
                    "id": HISTORY_ID,
                    "price": utils.usd(PRICE),
                    "shares": 1,
                    "symbol": SYMBOL,
                    "transacted": transaction_timestamp,
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

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertDictEqual(expected_results, response.json)


if __name__ == "__main__":
    unittest.main()
