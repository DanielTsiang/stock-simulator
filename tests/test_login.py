import sys
import unittest
from http import HTTPStatus
from pathlib import Path
from unittest import mock

from werkzeug.security import check_password_hash

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import (
    TEST1,
    ApplicationTestBase,
    app,
    captured_templates,
    db,
)


class LoginTest(ApplicationTestBase):
    def test_get_login(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # WHEN
                response = test_client.get("/login")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("login.html", template.name)

    def test_post_login_success(self):
        # GIVEN
        payload = {"username": TEST1, "password": TEST1}

        # WHEN
        with app.test_client() as test_client:
            response = test_client.post("/login", data=payload)
        users = db.execute("SELECT * FROM users WHERE username = ?", TEST1)

        # THEN
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/", response.location)
        self.assertEqual(1, len(users))
        self.assertTrue(check_password_hash(users[0]["hash"], TEST1))

    @mock.patch("routes.login.flash")
    def test_post_login_user_not_found(self, mock_flash):
        # GIVEN
        random_string = "random123"
        payload = {"username": random_string, "password": random_string}

        # WHEN
        with app.test_client() as test_client:
            response = test_client.post("/login", data=payload)
        users = db.execute("SELECT * FROM users WHERE username = ?", random_string)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(0, len(users))
        mock_flash.assert_called_once_with("Username does not exist", "danger")

    @mock.patch("routes.login.flash")
    def test_post_login_incorrect_password(self, mock_flash):
        # GIVEN
        random_string = "random123"
        payload = {"username": TEST1, "password": random_string}

        # WHEN
        with app.test_client() as test_client:
            response = test_client.post("/login", data=payload)
        users = db.execute("SELECT * FROM users WHERE username = ?", TEST1)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(1, len(users))
        self.assertTrue(check_password_hash(users[0]["hash"], TEST1))
        mock_flash.assert_called_once_with("Incorrect password", "danger")

    def test_get_logout(self):
        # WHEN
        with app.test_client() as test_client:
            response = test_client.get("/logout")

        # THEN
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/login", response.location)


if __name__ == "__main__":
    unittest.main()
