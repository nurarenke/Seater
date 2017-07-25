import server
import unittest
from model import connect_to_db, db, example_data, User, Attendee, Event, Table, SeatingRelationship
from assignments import table_assignments
from faker import Factory
from seed import store_users, 


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
        # In case this is run more than once, empty out existing data
        Attendee.query.delete()
        Table.query.delete()
        Event.query.delete()
        User.query.delete()
        SeatingRelationship.query.delete()

        # add fake users to database
        store_users()

        # grab the first user 
        self.test_event_owner = User.query.first()

        # add a fake event to the database
        test_gala_dinner = Event(event_name='Test Gala Dinner',
                    event_description='Testing', 
                    location='Testing')

        # match the user id to the event
        test_gala_dinner.user = self.test_event_owner

        # add attendees to the event
        store_attendees(test_gala_dinner)

        # commit our changes and add the event
        db.session.add(test_gala_dinner)
        db.session.commit()

        test_user = User.query.filter_by(email = 'nura@gmail.com').first()

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