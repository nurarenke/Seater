import server
import unittest
from model import connect_to_db, db, example_data, User, Attendee, Event, Table, SeatingRelationship
from assignments import table_assignments

# import doctest

# def load_tests(loader, tests, ignore):
#     """Also run our doctests and file-based doctests."""

#     tests.addTests(doctest.DocTestSuite(server))
#     # tests.addTests(doctest.DocFileSuite("tests.txt"))
#     return tests

class HomepageServerRoutesTestCase(unittest.TestCase):
    '''Tests to see what pages you see when logged out'''

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
    '''Tests to see what pages you see when logged in'''

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
        """Set up fake database and populate it"""

        # Get the Flask test client
        self.client = server.app.test_client()
        server.app.config['TESTING'] = True
        server.app.config['SECRET_KEY'] = "Lava12#$!!"

        # Connect to test database
        connect_to_db(server.app, "postgresql:///testdb")

        # Create tables and add sample data
        db.create_all()
        example_data()

        # Query the database
        test_user = User.query.filter_by(email = 'test@testemail.com').first()
        self.test_event = Event.query.filter_by(event_description='Testing').first()
        self.pocohontas = Attendee.query.filter_by(first_name = 'Pocohontas').first()
        self.john = Attendee.query.filter_by(first_name = 'John').first()
        self.test_table = Table.query.filter_by(table_name = 'Test Table').first()

        with self.client as c:
            with c.session_transaction() as se:
                se['user_id'] = test_user.user_id
                se['name'] = 'foo'

    def tearDown(self):
        """Log the user out and delete tables from database"""

        db.session.close()
        db.drop_all()

        with self.client as c:
            with c.session_transaction() as se:
                se.pop('user_id')
                se.pop('name')

    def test_events_list(self):
        """Test events page."""
    
        result = self.client.get("/events")
        self.assertIn('Test Event', result.data)

    def test_attendee_list(self):
        """Test attendee page."""
    
        result = self.client.get("/event={}/event-info/".format(self.test_event.event_id))
        self.assertIn('Pocohontas', result.data)
        self.assertIn('John Smith', result.data)

    def test_table_assignments_display(self):
        '''Test table assignments display'''

        # make the assignments
        self.client.post('/event={}/table-assignments/'.format(
            self.test_event.event_id))

        # verify the assignments
        result = self.client.get('/event={}/table-assignments/'.format(
            self.test_event.event_id))

        self.assertIn('Test Table', result.data)
        self.assertIn('<li>Smith, John</li>', result.data)
        self.assertIn('<li>Chiefess, Pocohontas</li>', result.data)


if __name__ == '__main__':
    # run our tests
    unittest.main()