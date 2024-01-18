import sys
from http import HTTPStatus
from pathlib import Path

import pytest

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())

import utils
from conftest import DEFAULT_CASH, captured_templates


def test_apology(app):
    # GIVEN
    with app.test_client() as test_client:
        with captured_templates(app) as templates:
            # WHEN
            response = test_client.get("/non-existent-page")
            template, context = templates[0]

    # THEN
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert template.name == "apology.html"
    assert context["top"] == "404 error"
    assert context["bottom"] == "Not-Found"


def test_login_required(app):
    # GIVEN
    with app.test_client() as test_client:
        # WHEN
        # Attempt to reach index page without logging in
        response = test_client.get("/")

    # THEN
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "/login"


def test_all_symbols():
    # WHEN
    symbols_data_stripped, symbols_only_data, symbols_list = utils.all_symbols()

    # THEN
    assert len(symbols_data_stripped) > 0
    assert len(symbols_only_data) > 0
    assert len(symbols_list) > 0


def test_usd():
    # GIVEN
    expected_usd_value = "$10,000.00"

    # WHEN
    usd_value = utils.usd(DEFAULT_CASH)

    # THEN
    assert usd_value == expected_usd_value


def test_datetimeformat():
    # GIVEN
    datetime_string = "2021-03-20 21:35:59"
    expected_formatted_dt_string = "20-03-2021 21:35:59"

    # WHEN
    formatted_dt_string = utils.datetimeformat(datetime_string)

    # THEN
    assert formatted_dt_string == expected_formatted_dt_string


if __name__ == "__main__":
    pytest.main([__file__])
