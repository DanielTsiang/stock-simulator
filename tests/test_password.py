import sys
import unittest
from http import HTTPStatus
from pathlib import Path

from werkzeug.security import check_password_hash

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import (
    TEST1,
    TEST2,
    USER_ID2,
    ApplicationTestBase,
    app,
    captured_templates,
    db,
)


class PasswordTest(ApplicationTestBase):
    def test_get_password(self):
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
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual("password.html", template.name)

    def test_put_password(self):
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

        rows = db.execute("SELECT hash FROM users WHERE id = ?", USER_ID2)
        hashed_password = rows[0]["hash"]

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)
        self.assertTrue(check_password_hash(hashed_password, TEST2))

    def test_post_password_check(self):
        # GIVEN
        payload = {"old_password": TEST1}

        # WHEN
        with app.test_client() as test_client:
            # Mock user logged in
            with test_client.session_transaction() as session:
                session["user_id"] = USER_ID2
            response = test_client.post("/password_check", data=payload)

        # THEN
        self.assertEqual(HTTPStatus.OK, response.status_code)
        self.assertEqual(True, response.json)


if __name__ == "__main__":
    unittest.main()
