import sys
import unittest
from http import HTTPStatus
from pathlib import Path

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from routes.symbols import symbols_data
from tests.application_test_base import (
    SYMBOL,
    USER_ID2,
    ApplicationTestBase,
    app,
    captured_templates,
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

    def test_get_symbol_check(self):
        # GIVEN
        payload = {"symbol_quote": SYMBOL}

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/symbol_check", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)

    def test_get_eligible_symbols(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # Mock user logged in
                with test_client.session_transaction() as session:
                    session["user_id"] = USER_ID2
                # WHEN
                response = test_client.get("/eligible_symbols")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("symbols.html", template.name)

    def test_get_symbols_json(self):
        # GIVEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            # WHEN
            response = test_client.get("/symbols_json")

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertDictEqual({"data": symbols_data}, response.json)


if __name__ == "__main__":
    unittest.main()
