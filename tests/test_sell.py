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
    SYMBOL,
    USER_ID2,
    ApplicationTestBase,
    app,
)


class SellTest(ApplicationTestBase):
    @mock.patch("application.SQL.execute")
    @mock.patch("routes.sell.lookup")
    def test_put_sell(self, mock_lookup, mock_db_execute):
        # GIVEN
        payload = {"symbol_sell": SYMBOL, "shares_sell": 1}

        mock_lookup.return_value = LOOKUP_RETURN
        mock_db_execute.side_effect = [
            [{"shares_count": 1}],
            [{"cash": DEFAULT_CASH}],
            1,
            94,
            1,
        ]

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.put("/sell", data=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)

    def test_get_sell_check(self):
        # GIVEN
        payload = {"symbol_sell": SYMBOL, "shares_sell": 1}

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/sell_check", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)

    def test_get_sell_json(self):
        # GIVEN
        payload = {"q": "GOOG"}

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/sell_json", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual({"symbol": SYMBOL}, response.json["symbols"][0])


if __name__ == "__main__":
    unittest.main()
