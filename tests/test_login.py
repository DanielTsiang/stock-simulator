import sys
from http import HTTPStatus
from pathlib import Path

import pytest
from werkzeug.security import check_password_hash

from conftest import TEST1, captured_templates

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_get_login(app):
    # GIVEN
    with app.test_client() as test_client:
        with captured_templates(app) as templates:
            # WHEN
            response = test_client.get("/login")
            template, context = templates[0]

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert template.name == "login.html"


def test_post_login_success(app, db):
    # GIVEN
    payload = {"username": TEST1, "password": TEST1}

    # WHEN
    with app.test_client() as test_client:
        response = test_client.post("/login", data=payload)
    users = db.execute("SELECT * FROM users WHERE username = ?", TEST1)

    # THEN
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "/"
    assert len(users) == 1
    assert check_password_hash(users[0]["hash"], TEST1)


def test_post_login_user_not_found(app, db, mocker):
    # GIVEN
    random_string = "random123"
    payload = {"username": random_string, "password": random_string}

    mocked_flash = mocker.patch("routes.login.flash")

    # WHEN
    with app.test_client() as test_client:
        response = test_client.post("/login", data=payload)
    users = db.execute("SELECT * FROM users WHERE username = ?", random_string)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert len(users) == 0
    mocked_flash.assert_called_once_with("Username does not exist", "danger")


def test_post_login_incorrect_password(app, db, mocker):
    # GIVEN
    random_string = "random123"
    payload = {"username": TEST1, "password": random_string}

    mocked_flash = mocker.patch("routes.login.flash")

    # WHEN
    with app.test_client() as test_client:
        response = test_client.post("/login", data=payload)
    users = db.execute("SELECT * FROM users WHERE username = ?", TEST1)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert len(users) == 1
    assert not check_password_hash(users[0]["hash"], random_string)
    mocked_flash.assert_called_once_with("Incorrect password", "danger")


def test_get_logout(app):
    # WHEN
    with app.test_client() as test_client:
        response = test_client.get("/logout")

    # THEN
    assert response.status_code == HTTPStatus.FOUND
    assert response.location == "/login"


if __name__ == "__main__":
    pytest.main([__file__])
