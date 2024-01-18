import sys
from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path

import pytest

from conftest import HISTORY_ID, PRICE, SYMBOL, USER_ID1, USER_ID2, captured_templates

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_get_history(app):
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
    assert response.status_code == HTTPStatus.OK
    assert template.name == "history.html"


def test_delete_history(app, db):
    # GIVEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID1
        # WHEN
        response = test_client.delete("/history")

    # Obtain history information for logged-in user
    transactions = db.execute(
        "SELECT * FROM history WHERE user_id = ? ORDER BY transacted DESC", USER_ID1
    )

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == True
    assert transactions == []


def test_get_history_json(app, mocker):
    import utils

    # GIVEN
    transaction_timestamp = datetime.now(timezone.utc).strftime("%d-%m-%Y %H:%M:%S")

    mocked_datetimeformat = mocker.patch("routes.history.datetimeformat")
    mocked_datetimeformat.return_value = transaction_timestamp

    expected_results = {
        "data": [
            {
                "id": HISTORY_ID,
                "price": utils.usd(PRICE),
                "shares": 1,
                "symbol": SYMBOL,
                "transacted": transaction_timestamp,
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
    assert response.status_code == HTTPStatus.OK
    assert response.json == expected_results


if __name__ == "__main__":
    pytest.main([__file__])
