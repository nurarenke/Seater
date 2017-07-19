import server
import unittest
from model import connect_to_db, db, example_data
# import doctest



# def load_tests(loader, tests, ignore):
#     """Also run our doctests and file-based doctests."""

#     tests.addTests(doctest.DocTestSuite(server))
#     # tests.addTests(doctest.DocFileSuite("tests.txt"))
#     return tests

class NavigationServerRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = "Lava12#$!!"

    def test_navigation_logged_out(self):

        result = self.client.get('/')
        self.assertIn('Register', result.data)
        self.assertIn('Login', result.data)
        self.assertNotIn('View All Events', result.data)
        self.assertNotIn('Logout', result.data)

class FlaskTestsDatabase(unittest.TestCasee):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Connect to test database
        connect_to_db(app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_some_db_thing(self):
        """Some database test..."




if __name__ == '__main__':
    # run our tests
    unittest.main()