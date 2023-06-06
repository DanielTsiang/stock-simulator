import sys
import unittest
from http import HTTPStatus
from pathlib import Path
from unittest import mock

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import (
    DEFAULT_CASH,
    LOOKUP_RETURN,
    NAME,
    NEW_PRICE,
    SYMBOL,
    USER_ID2,
    ApplicationTestBase,
    app,
    captured_templates,
    db,
)


class IndexTest(ApplicationTestBase):
    def test_get_index(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # Mock user logged in
                with test_client.session_transaction() as session:
                    session["user_id"] = USER_ID2
                # WHEN
                response = test_client.get("/")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("index.html", template.name)

    @mock.patch("routes.index.lookup")
    def test_get_index_json(self, mock_lookup):
        # GIVEN
        mock_lookup.return_value = LOOKUP_RETURN

        expected_response = {
            "cash_data": DEFAULT_CASH / 100,
            "shares_data": [
                {
                    "name": NAME,
                    "price": NEW_PRICE,
                    "shares_count": 1,
                    "symbol": SYMBOL,
                    "total": NEW_PRICE,
                    "user_id": USER_ID2,
                }
            ],
        }

        expected_shares = [
            {
                "user_id": USER_ID2,
                "symbol": SYMBOL,
                "name": NAME,
                "shares_count": 1,
                "price": int(NEW_PRICE * 100),
                "total": int(NEW_PRICE * 100),
            }
        ]

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/index_json")

        updated_shares = db.execute(
            "SELECT * FROM shares WHERE user_id = ? AND symbol = ?", USER_ID2, SYMBOL
        )

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected_response, response.json)
        self.assertEqual(expected_shares, updated_shares)


if __name__ == "__main__":
    unittest.main()
