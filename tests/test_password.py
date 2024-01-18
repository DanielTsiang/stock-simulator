import sys
from http import HTTPStatus
from pathlib import Path

import pytest
from werkzeug.security import check_password_hash

from conftest import TEST1, TEST2, TEST3, USER_ID2, USER_ID3, captured_templates

# Append root directory to list of searched paths
sys.path.append(Path(__file__).parents[1].as_posix())


def test_get_password(app):
    # GIVEN
    with app.test_client() as test_client:
        with captured_templates(app) as templates:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            # WHEN
            response = test_client.get("/password")
            template, context = templates[0]

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert template.name == "password.html"


def test_put_password(app, db):
    # GIVEN
    payload = {
        "old_password": TEST1,
        "new_password": TEST2,
        "confirmation": TEST2,
    }

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID2
        response = test_client.put("/password", data=payload)

    user_hashes = db.execute("SELECT hash FROM users WHERE id = ?", USER_ID2)
    hashed_password = user_hashes[0]["hash"]

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == True
    assert check_password_hash(hashed_password, TEST2)


def test_post_password_check(app):
    # GIVEN
    payload = {"old_password": TEST3}

    # WHEN
    with app.test_client() as test_client:
        # Mock user logged in
        with test_client.session_transaction() as session:
            session["user_id"] = USER_ID3
        response = test_client.post("/password_check", data=payload)

    # THEN
    assert response.status_code == HTTPStatus.OK
    assert response.json == True


if __name__ == "__main__":
    pytest.main([__file__])
