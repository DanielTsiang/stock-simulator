import sqlite3
import sys
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

import pytest
from flask import template_rendered

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())

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
TEST3 = "test3"
USER_ID1 = 1
USER_ID2 = 2
USER_ID3 = 3

LOOKUP_RETURN = {
    "GOOGL": {
        "symbol": SYMBOL,
        "longName": NAME,
        "currentPrice": NEW_PRICE,
    }
}


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


@pytest.fixture(autouse=True, scope="session")
def setup():
    # Set up test database
    base_path = Path(__file__).parent
    test_db_path = base_path / "test.db"
    if test_db_path.exists():
        test_db_path.unlink()
    test_db = sqlite3.connect(test_db_path.as_posix())
    source_db = sqlite3.connect((base_path / "simulator.backup.db").as_posix())
    source_db.backup(test_db)

    # Set up environment variables
    env_patcher = mock.patch.dict(
        "os.environ", {"DATABASE_URL": f"sqlite:///{test_db_path}", "API_KEY": "123456"}
    )
    env_patcher.start()

    from application import app, db

    # Register users
    payload1 = {"username": TEST1, "password": TEST1, "confirmation": TEST1}
    payload2 = {"username": TEST3, "password": TEST3, "confirmation": TEST3}
    with app.test_client() as test_client:
        test_client.post("/register", data=payload1)
        test_client.post("/register", data=payload2)
    db.execute("UPDATE users SET id = ? WHERE username = ?", USER_ID2, TEST1)
    db.execute("UPDATE users SET id = ? WHERE username = ?", USER_ID3, TEST3)

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

    yield

    # Tear down
    if test_db_path.exists():
        test_db_path.unlink()

    env_patcher.stop()


@pytest.fixture
def app():
    from application import app

    return app


@pytest.fixture
def db():
    from application import db

    return db
