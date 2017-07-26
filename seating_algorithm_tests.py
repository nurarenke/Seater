import server
import unittest
from model import connect_to_db, db, example_data, User, Attendee, Event, Table, SeatingRelationship
from assignments import table_assignments
from faker import Factory
from seed import create_example_data


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

        create_example_data()

        test_user = User.query.filter_by(email = 'nura@gmail.com').first()
        self.test_event = Event.query.filter_by(event_description='Fundraiser').first()
        self.event_id = self.test_event.event_id

        # create list of attendee_ids
        self.attendees = []
        for attendee in db.session.query(Attendee).filter(Attendee.event_id == self.event_id).all():
            self.attendees.append(attendee.attendee_id)

        #create dictionary of table ids
        self.tables = {}
        self.total_seats = 0;
        for table in db.session.query(Table).filter(Table.event_id == self.event_id).all():
            self.tables[table.table_id] = table.max_seats
            self.total_seats += table.max_seats

        self.attendee_six = Attendee.query.filter_by(attendee_id = 6).first()
        self.attendee_seven = Attendee.query.filter_by(attendee_id = 7).first()


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

    def test_table_assignments(self):
        result = table_assignments(self.event_id, self.attendees, 
            self.tables, self.total_seats)

        # table_id=[]
        # seated_attendees=[]

        # for table_id, seated_attendees in result.items():
        #     table_id.append(table_id)
        #     seated_attendees.append(seated_attendees)

        self.assertNotEqual(self.attendee_six.table_id, self.attendee_six.table_id)





if __name__ == '__main__':
    # run our tests
    unittest.main()