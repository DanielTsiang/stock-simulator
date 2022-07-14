from http import HTTPStatus
from pathlib import Path
import sys
import unittest

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import ApplicationTestBase, NEW_CASH, USER_ID2, app, db


class CashTest(ApplicationTestBase):
    def test_put_cash(self):
        # GIVEN
        payload = {"cash": NEW_CASH}

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.put("/cash", data=payload)
        cash = db.execute("SELECT cash FROM users WHERE id = ?", USER_ID2)[0]["cash"]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)
        self.assertEqual(NEW_CASH, cash)


if __name__ == "__main__":
    unittest.main()
