import sys
from http import HTTPStatus
from pathlib import Path

import pytest

from conftest import SYMBOL, USER_ID2, captured_templates

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_get_select_json(app):
    # GIVEN
    payload = {"q": SYMBOL[:-1]}

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        response = test_client.get("/select_json", query_string=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json["symbols"][1] == {"Symbol": SYMBOL}


def test_get_symbol_check(app):
    # GIVEN
    payload = {"symbol_quote": SYMBOL}

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        response = test_client.get("/symbol_check", query_string=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == True


def test_get_eligible_symbols(app):
    # GIVEN
    with app.test_client() as test_client:
        with captured_templates(app) as templates:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            # WHEN
            response = test_client.get("/eligible_symbols")
            template, context = templates[0]

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert template.name == "symbols.html"


def test_get_symbols_json(app):
    from routes.symbols import symbols_data

    # GIVEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        # WHEN
        response = test_client.get("/symbols_json")

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == {"data": symbols_data}


if __name__ == "__main__":
    pytest.main([__file__])
