import sys
from http import HTTPStatus
from pathlib import Path

import pytest

from conftest import LOOKUP_RETURN, SYMBOL, USER_ID2

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_get_quote(app, mocker):
    # GIVEN
    payload = {"symbol_quote": SYMBOL}
    mocked_lookup = mocker.patch("routes.quote.lookup")
    mocked_lookup.return_value = LOOKUP_RETURN

    expected_quote = {"QUOTED": LOOKUP_RETURN, "symbol": SYMBOL}

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        response = test_client.get("/quote", query_string=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == expected_quote


if __name__ == "__main__":
    pytest.main([__file__])
