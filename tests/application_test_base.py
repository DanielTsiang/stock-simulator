import logging
import os
import sqlite3
import sys
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from flask import template_rendered

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

# Disable requests library debug logging
logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

# Config
DEFAULT_CASH = 1000000
HISTORY_ID = 93
NAME = "Alphabet Inc"
NEW_CASH = 888888
NEW_PRICE = 2174.53
PRICE = 2129.78
SYMBOL = "GOOGL"
TEST1 = "test1"
TEST2 = "test2"
USER_ID1 = 1
USER_ID2 = 2

LOOKUP_RETURN = {
    "GOOGL": {
        "symbol": SYMBOL,
        "longName": NAME,
        "currentPrice": NEW_PRICE,
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


class ApplicationTestBase(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        base_path = Path(__file__).parent
        cls.test_db_path = os.path.join(base_path, "test.db")
        if not os.path.exists(cls.test_db_path):
            setUp()

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
            SYMBOL,
            1,
            PRICE,
        )
        db.execute(
            "UPDATE history SET id = ? WHERE user_id = ? AND symbol = ? AND transacted = datetime('now')",
            HISTORY_ID,
            USER_ID2,
            SYMBOL,
        )

        # Insert share into shares table
        db.execute(
            "INSERT INTO shares VALUES (?, ?, ?, ?, ?, ?)",
            USER_ID2,
            SYMBOL,
            NAME,
            1,
            PRICE,
            PRICE,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        env_patcher.stop()
