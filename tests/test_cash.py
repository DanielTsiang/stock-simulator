import sys
from http import HTTPStatus
from pathlib import Path

import pytest

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())

from conftest import NEW_CASH, USER_ID3


def test_put_cash(app, db):
    # GIVEN
    payload = {"cash": NEW_CASH}

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID3
        response = test_client.put("/cash", data=payload)
    cash = db.execute("SELECT cash FROM users WHERE id = ?", USER_ID3)[0]["cash"]

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == True
    assert cash == NEW_CASH * 100


if __name__ == "__main__":
    pytest.main([__file__])
