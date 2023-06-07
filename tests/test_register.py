import sys
import unittest
from http import HTTPStatus
from pathlib import Path

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import (
    TEST1,
    TEST2,
    ApplicationTestBase,
    app,
    captured_templates,
    db,
)


class RegisterTest(ApplicationTestBase):
    def test_get_register(self):
        # GIVEN
        with app.test_client() as test_client:
            with captured_templates(app) as templates:
                # WHEN
                response = test_client.get("/register")
                template, context = templates[0]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("register.html", template.name)

    def test_post_register(self):
        # GIVEN
        payload = {"username": TEST2, "password": TEST2, "confirmation": TEST2}

        # WHEN
        with app.test_client() as test_client:
            response = test_client.post("/register", data=payload)
        rows = db.execute("SELECT username FROM users WHERE username = ?", TEST2)
        username = rows[0]["username"]

        # THEN
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/", response.location)
        self.assertEqual(TEST2, username)

    def test_get_username_check(self):
        # GIVEN
        payload = {"username": TEST1}

        # WHEN
        with app.test_client() as test_client:
            response = test_client.get("/username_check", query_string=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(False, response.json)


if __name__ == "__main__":
    unittest.main()
