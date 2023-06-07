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


class BuyTest(ApplicationTestBase):
    @mock.patch("application.SQL.execute")
    @mock.patch("routes.buy.lookup")
    def test_put_buy(self, mock_lookup, mock_db_execute):
        # GIVEN
        payload = {"symbol_buy": SYMBOL, "shares_buy": 1}

        mock_lookup.return_value = LOOKUP_RETURN
        mock_db_execute.side_effect = [
            [{"cash": DEFAULT_CASH}],
            1,
            93,
            [{"shares_count": 1}],
            1,
        ]

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.put("/buy", data=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)

    @mock.patch("routes.buy.lookup")
    def test_get_buy_check(self, mock_lookup):
        # GIVEN
        payload = {"symbol_buy": SYMBOL, "shares_buy": 1}
        mock_lookup.return_value = LOOKUP_RETURN

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/buy_check", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)


if __name__ == "__main__":
    unittest.main()
