import sys
from http import HTTPStatus
from pathlib import Path

import pytest

from conftest import DEFAULT_CASH, LOOKUP_RETURN, SYMBOL, USER_ID2

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_put_sell(app, mocker):
    # GIVEN
    payload = {"symbol_sell": SYMBOL, "shares_sell": 1}

    mocked_lookup = mocker.patch("routes.sell.lookup")
    mocked_lookup.return_value = LOOKUP_RETURN

    mocked_db_execute = mocker.patch("application.SQL.execute")
    mocked_db_execute.side_effect = [
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
    assert response.status_code == HTTPStatus.OK
    assert response.json == True


def test_get_sell_check(app):
    # GIVEN
    payload = {"symbol_sell": SYMBOL, "shares_sell": 1}

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        response = test_client.get("/sell_check", query_string=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == True


def test_get_sell_json(app):
    # GIVEN
    payload = {"q": SYMBOL[:-1]}

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        response = test_client.get("/sell_json", query_string=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == {"symbols": [{"symbol": SYMBOL}]}


if __name__ == "__main__":
    pytest.main([__file__])
