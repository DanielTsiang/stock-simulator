import sys
import unittest
from http import HTTPStatus
from pathlib import Path

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

import utils
from tests.application_test_base import DEFAULT_CASH, app, captured_templates


class UtilsTest(unittest.TestCase):
    def test_apology(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # WHEN
                response = test_client.get("/non-existent-page")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.NOT_FOUND, response.status_code)
        self.assertEqual("apology.html", template.name)
        self.assertEqual("404 error", context["top"])
        self.assertEqual("Not-Found", context["bottom"])

    def test_login_required(self):
        # GIVEN
        with app.test_client() as test_client:
            # WHEN
            # Attempt to reach index page without logging in
            response = test_client.get("/")

        # THEN
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/login", response.location)

    def test_all_symbols(self):
        # WHEN
        symbols_data_stripped, symbols_only_data, symbols_list = utils.all_symbols()

        # THEN
        self.assertGreater(len(symbols_data_stripped), 0)
        self.assertGreater(len(symbols_only_data), 0)
        self.assertGreater(len(symbols_list), 0)

    def test_usd(self):
        # GIVEN
        expected_usd_value = "$10,000.00"

        # WHEN
        usd_value = utils.usd(DEFAULT_CASH)

        # THEN
        self.assertEqual(expected_usd_value, usd_value)

    def test_datetimeformat(self):
        # GIVEN
        datetime_string = "2021-03-20 21:35:59"
        expected_formatted_dt_string = "20-03-2021 21:35:59"

        # WHEN
        formatted_dt_string = utils.datetimeformat(datetime_string)

        # THEN
        self.assertEqual(expected_formatted_dt_string, formatted_dt_string)


if __name__ == "__main__":
    unittest.main()
