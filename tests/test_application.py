from contextlib import contextmanager
from datetime import datetime, timezone
from flask import template_rendered
from http import HTTPStatus
from pathlib import Path
from unittest import mock
import sqlite3
import sys
import os
import unittest


# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

# Config
DEFAULT_CASH = 10000
HISTORY_ID = 93
NAME1 = "Alphabet Inc"
NEW_PRICE = 2174.53
PRICE = 2129.78
SYMBOL1 = "GOOGL"
TEST1 = "test1"
TEST2 = "test2"
USER_ID1 = 1
USER_ID2 = 2

LOOKUP_RETURN = {
    "GOOGL": {
        "quote": {
            "symbol": SYMBOL1,
            "companyName": NAME1,
            "latestPrice": NEW_PRICE,
        }
    }
}


def setUp():
    # Set up test database
    base_path = Path(__file__).parent
    test_db_path = os.path.join(base_path, "test.db")
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    test_db = sqlite3.connect(test_db_path)
    source_db = sqlite3.connect(os.path.join(base_path, "simulator.backup.db"))
    source_db.backup(test_db)

    # Set up environment variables
    env_patcher = mock.patch.dict(
        "os.environ", {"DATABASE_URL": f"sqlite:///{test_db_path}", "API_KEY": "123456"}
    )
    env_patcher.start()
    return env_patcher


env_patcher = setUp()
from application import app, db
import helpers


@contextmanager
def captured_templates(app):
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


class ApplicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.login_payload = {"username": TEST1, "password": TEST1}

        # Register user
        payload = {"username": TEST1, "password": TEST1, "confirmation": TEST1}
        with app.test_client() as test_client:
            test_client.post("/register", data=payload)
        db.execute("UPDATE users SET id = ? WHERE username = ?", USER_ID2, TEST1)

        # Insert buy log into history table
        db.execute(
            "INSERT INTO history (user_id, symbol, shares, price, transacted) VALUES (?, ?, ?, ?, datetime('now'))",
            USER_ID2,
            SYMBOL1,
            1,
            PRICE,
        )
        db.execute(
            "UPDATE history SET id = ? WHERE user_id = ? AND symbol = ? AND transacted = datetime('now')",
            HISTORY_ID,
            USER_ID2,
            SYMBOL1,
        )

        # Insert share into shares table
        db.execute(
            "INSERT INTO shares VALUES (?, ?, ?, ?, ?, ?)",
            USER_ID2,
            SYMBOL1,
            NAME1,
            1,
            PRICE,
            PRICE,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        base_path = Path(__file__).parent
        test_db_path = os.path.join(base_path, "test.db")
        if os.path.exists(test_db_path):
            os.remove(test_db_path)
        env_patcher.stop()

    def test_get_login(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # WHEN
                response = test_client.get("/login")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("login.html", template.name)

    def test_get_register(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # WHEN
                response = test_client.get("/register")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("register.html", template.name)

    def test_post_register(self):
        # GIVEN
        payload = {"username": TEST2, "password": TEST2, "confirmation": TEST2}

        # WHEN
        with app.test_client() as test_client:
            response = test_client.post("/register", data=payload)
        username = db.execute("SELECT username FROM users WHERE username = ?", TEST2)[
            0
        ]["username"]

        # THEN
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/", response.location)
        self.assertEqual(TEST2, username)

    def test_get_logout(self):
        # WHEN
        with app.test_client() as test_client:
            response = test_client.get("/logout")

        # THEN
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/login", response.location)

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

    @mock.patch("application.lookup")
    def test_get_index_json(self, mock_lookup):
        # GIVEN
        mock_lookup.return_value = LOOKUP_RETURN

        expected_response = {
            "cash_data": DEFAULT_CASH,
            "shares_data": [
                {
                    "name": NAME1,
                    "price": NEW_PRICE,
                    "shares_count": 1,
                    "symbol": SYMBOL1,
                    "total": NEW_PRICE,
                    "user_id": USER_ID2,
                }
            ],
        }

        expected_shares = [
            {
                "user_id": USER_ID2,
                "symbol": SYMBOL1,
                "name": NAME1,
                "shares_count": 1,
                "price": NEW_PRICE,
                "total": NEW_PRICE,
            }
        ]

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/index_json")

        updated_shares = db.execute(
            "SELECT * FROM shares WHERE user_id = ? AND symbol = ?", USER_ID2, SYMBOL1
        )

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(expected_response, response.json)
        self.assertEqual(expected_shares, updated_shares)

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

    @mock.patch("application.SQL.execute")
    @mock.patch("application.lookup")
    def test_put_buy(self, mock_lookup, mock_db_execute):
        # GIVEN
        payload = {"symbol_buy": SYMBOL1, "shares_buy": 1}

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

    @mock.patch("application.lookup")
    def test_get_buy_check(self, mock_lookup):
        # GIVEN
        payload = {"symbol_buy": SYMBOL1, "shares_buy": 1}
        mock_lookup.return_value = LOOKUP_RETURN

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.get("/buyCheck", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)

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

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)

        # Obtain history information for logged-in user
        transactions = db.execute(
            "SELECT * FROM history WHERE user_id = ? ORDER BY transacted DESC", USER_ID1
        )
        self.assertEqual([], transactions)

    def test_get_history_json(self):
        # GIVEN
        expected_history = {
            "data": [
                {
                    "id": HISTORY_ID,
                    "price": helpers.usd(PRICE),
                    "shares": 1,
                    "symbol": SYMBOL1,
                    "transacted": datetime.now(timezone.utc).strftime(
                        "%d-%m-%Y %H:%M:%S"
                    ),
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
        self.assertEqual(expected_history, response.json)


if __name__ == "__main__":
    unittest.main()
