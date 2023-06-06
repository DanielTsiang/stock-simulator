import sys
import unittest
from http import HTTPStatus
from pathlib import Path
from unittest import mock

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import (
    LOOKUP_RETURN,
    SYMBOL,
    USER_ID2,
    ApplicationTestBase,
    app,
)


class QuoteTest(ApplicationTestBase):
    @mock.patch("routes.quote.lookup")
    def test_get_quote(self, mock_lookup):
        # GIVEN
        payload = {"symbol_quote": SYMBOL}
        mock_lookup.return_value = LOOKUP_RETURN
        expected_quote = {"QUOTED": LOOKUP_RETURN, "symbol": SYMBOL}

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/quote", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected_quote, response.json)


if __name__ == "__main__":
    unittest.main()
