import unittest

from server import app
from model import db, connect_to_db

class NearSitedTests(unittest.TestCase):
    """Tests for my NearSited site."""

    def setUp(self):
        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_homepage(self):
        result = self.client.get('/')
        self.assertIn("welcome", result.data)

    def test_register_form(self):
        result = self.client.get('/register')
        self.assertIn("First Name", result.data)

    def test_login_form(self):
        result = self.client.get('/login')
        self.assertIn("Email address", result.data)

    def test_site_search(self):
        result = self.client.get(('/sites?search=San+Francisco'), 
                                follow_redirects=True)
        self.assertIn('Grandview Park', result.data)


if __name__ == "__main__":
    unittest.main()