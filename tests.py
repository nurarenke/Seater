import server
import unittest
from model import connect_to_db, db, example_data
# import doctest



# def load_tests(loader, tests, ignore):
#     """Also run our doctests and file-based doctests."""

#     tests.addTests(doctest.DocTestSuite(server))
#     # tests.addTests(doctest.DocFileSuite("tests.txt"))
#     return tests

class HomepageServerRoutesTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = "Lava12#$!!"

    def test_homepage_logged_out(self):

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<a href="/">Register</a>', result.data)
        self.assertIn('<a href="/">Login</a>', result.data)
        self.assertNotIn('<a href="/events">View All Events</a>', result.data)
        self.assertNotIn('<a href="/logout">Logout</a>', result.data)

class HomepageServerRoutesLoggedInTestCase(unittest.TestCase):

    def setUp(self):
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = "Lava12#$!!"

        with self.client as c:
            with c.session_transaction() as se:
                se['user_id'] = 13
                se['username'] = 'foo'

    def test_homepage_logged_in(self):

        result = self.client.get('/')
        self.assertEqual(result.status_code, 200)
        self.assertIn('<a href="/events">View All Events</a>', result.data)
        self.assertIn('<a href="/logout">Logout</a>', result.data)
        self.assertNotIn('<a href="/">Register</a>', result.data)
        self.assertNotIn('<a href="/">Login</a>', result.data)

    # tear down by logging out
    def tearDown(self):

        with self.client as c:
            with c.session_transaction() as se:
                se.pop('user_id')
                se.pop('username')



class FlaskTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = "Lava12#$!!"

        # Connect to test database
        connect_to_db(server.app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        with self.client as c:
            with c.session_transaction() as se:
                se['user_id'] = 13
                se['username'] = 'foo'

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

        with self.client as c:
            with c.session_transaction() as se:
                se.pop('user_id')
                se.pop('username')

    def test_events_list(self):
        """Test events page."""
    
        result = self.client.get("/events")
        self.assertIn('Test Event', result.data)

    # def test_attendee_list(self):
    #     """Test attende page."""
    
    # result = self.client.get("/event=<int:event_id>/event-info/")
    #     self.assertIn('Test Event', result.data)




if __name__ == '__main__':
    # run our tests
    unittest.main()