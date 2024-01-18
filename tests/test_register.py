import sys
from http import HTTPStatus
from pathlib import Path

import pytest

from conftest import TEST1, TEST2, captured_templates

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_get_register(app):
    # GIVEN
    with app.test_client() as test_client:
        with captured_templates(app) as templates:
            # WHEN
            response = test_client.get("/register")
            template, context = templates[0]

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert template.name == "register.html"


def test_post_register(app, db):
    # GIVEN
    payload = {"username": TEST2, "password": TEST2, "confirmation": TEST2}

    # WHEN
    with app.test_client() as test_client:
        response = test_client.post("/register", data=payload)
    users = db.execute("SELECT username FROM users WHERE username = ?", TEST2)
    username = users[0]["username"]

    # THEN
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "/"
    assert username == TEST2


def test_get_username_check(app):
    # GIVEN
    payload = {"username": TEST1}

    # WHEN
    with app.test_client() as test_client:
        response = test_client.get("/username_check", query_string=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == False


if __name__ == "__main__":
    pytest.main([__file__])
