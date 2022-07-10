from http import HTTPStatus
from pathlib import Path
import sys
import unittest

# Append root directory to list of searched paths
sys.path.append(str(Path(__file__).parents[1]))

from tests.application_test_base import ApplicationTestBase, app, captured_templates


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

    def test_get_logout(self):
        # WHEN
        with app.test_client() as test_client:
            response = test_client.get("/logout")

        # THEN
        self.assertEqual(HTTPStatus.FOUND, response.status_code)
        self.assertEqual("/login", response.location)


if __name__ == "__main__":
    unittest.main()
