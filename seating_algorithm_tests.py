import server
import unittest
from model import connect_to_db, db, example_data, User, Attendee, Event, Table, SeatingRelationship
from assignments import table_assignments
from faker import Factory
from seed import create_fake_attendees

class TableAssignmentsTest(unittest.TestCase):
    '''Test a database of 50 attendees'''

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
        create_fake_attendees(50)