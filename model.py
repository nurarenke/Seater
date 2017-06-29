"""Models and database functions for Seater project."""

from flask_sqlalchemy import SQLAlchemy

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions

class User(db.Model):
    """User of seater website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    password = db.Column(db.String(64), nullable=False,)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s password=%s>" % (
            self.user_id, self.email, self.password)

class Event(db.Model):
    '''Event description'''

    __tablename__ = 'events'

    event_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    event_name = db.Column(db.String(64), nullable=False)
    event_description = db.Column(db.String(150), nullable=True)
    location = db.Column(db.String(50), nullable=True)
    time = db.Column(db.DateTime, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))

    user = db.relationship('User', 
                            backref=db.backref('events', order_by=event_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event event_id=%s event_name=%s event_description=%s>" % (
            self.event_id, self.event_name, self.event_description)

class Table(db.Model):
    '''Table description'''

    __tablename__ = 'tables'

    table_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    table_name = db.Column(db.String(64), nullable=True, unique=True)
    max_seats = db.Column(db.Integer, nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))

    event = db.relationship('Event', 
                            backref=db.backref('tables', order_by=table_id))

    user = db.relationship('User', 
                            backref=db.backref('tables', order_by=table_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Event table_id=%s table_name=%s max_seats=%s>" % (
            self.table_id, self.table_name, self.max_seats)

class Attendee(db.Model):
    '''Attendee of an event'''

    __tablename__ = 'attendees'

    attendee_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    attendee_email = db.Column(db.String(64), nullable=True)
    street = db.Column(db.String(64), nullable=True)
    city = db.Column(db.String(64), nullable=True)
    state = db.Column(db.String(64), nullable=True)
    zipcode = db.Column(db.Integer, nullable=True)
    vip_status = db.Column(db.Boolean, nullable=True)
    meal_request = db.Column(db.String(64), nullable=True)
    note = db.Column(db.String(100), nullable=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'))
    table_id = db.Column(db.Integer, db.ForeignKey('tables.table_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('User.user_id'))

    events = db.relationship('Event',
                            backref=db.backref('attendees', order_by=attendee_id))

    tables = db.relationship('Table', 
                            backref=db.backref('attendees', order_by=attendee_id))

    user = db.relationship('User', 
                            backref=db.backref('attendees', order_by=attendee_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Attendee attendee_id=%s first_name=%s last_name=%s>" % (
            self.attendee_id, self.first_name, self.last_name)

class SeatingRelationship(db.Model):
    '''create relationships between attendees in order to seat them'''

    __tablename__ = 'seating_relationships'

    seating_relationship_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    primary_attendee = db.Column(db.Integer, db.ForeignKey('attendees.attendee_id'))
    secondary_attendee = db.Column(db.Integer, db.ForeignKey('attendees.attendee_id'))
    relationship_code = db.Column(db.String(20), db.Enum('must_sit_with', 'want_to_sit_with', 'does_not_to_sit_with', name='relationship_types'))

    __table_args__ = (db.UniqueConstraint('primary_attendee', 'secondary_attendee', name='attendee_relationship'),)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<SeatingRelationship primary_attendee=%s secondary_attendee=%s relationship_code=%s>" % (
            self.primary_attendee, self.secondary_attendee, self.relationship_code)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PstgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///seater'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.
    from server import app
    connect_to_db(app)
    print "Connected to DB."

    db.create_all()
