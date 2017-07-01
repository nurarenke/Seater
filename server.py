"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Attendee, Event, Table, SeatingRelationship


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")

@app.route('/attendee-list')
def display_attendee_list():
    '''displays the list of attendees for a particular event'''

    event_id = 1
    attendees = Attendee.query.filter_by(event_id=event_id).all()

    return render_template('attendees_list.html', attendees=attendees)

@app.route('/attendee/<int:attendee_id>')
def attendee_detail(attendee_id):
    '''Show info about user.'''

    attendee = Attendee.query.get(attendee_id)

    event_id = 1
    attendees = Attendee.query.filter_by(event_id=event_id).all()

    return render_template("attendee.html", attendee=attendee, attendees=attendees)


@app.route('/attendee/<int:attendee_id>', methods=['POST'])
def update_relationship(attendee_id):
    '''update relationship of the user in the database'''

    secondary_attendee = request.form['secondary-attendee']

    relationship_code = request.form['relationship-code']

    relationship = SeatingRelationship(primary_attendee=attendee_id, 
        secondary_attendee=secondary_attendee, relationship_code=relationship_code)

    db.session.commit()

    return redirect('/attendee/<int:attendee_id>')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
