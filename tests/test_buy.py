import sys
from http import HTTPStatus
from pathlib import Path

import pytest

from conftest import DEFAULT_CASH, LOOKUP_RETURN, SYMBOL, USER_ID2

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_put_buy(app, mocker):
    # GIVEN
    payload = {"symbol_buy": SYMBOL, "shares_buy": 1}

    mocked_lookup = mocker.patch("routes.buy.lookup")
    mocked_lookup.return_value = LOOKUP_RETURN

    mocked_db_execute = mocker.patch("application.SQL.execute")
    mocked_db_execute.side_effect = [
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
    assert response.status_code == HTTPStatus.OK
    assert response.json == True


def test_get_buy_check(app, mocker):
    # GIVEN
    payload = {"symbol_buy": SYMBOL, "shares_buy": 1}

    mocked_lookup = mocker.patch("routes.buy.lookup")
    mocked_lookup.return_value = LOOKUP_RETURN

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        response = test_client.get("/buy_check", query_string=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == True


if __name__ == "__main__":
    pytest.main([__file__])
