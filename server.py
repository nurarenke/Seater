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

@app.route('/event-info')
def display_attendee_list():
    '''displays the list of attendees for a particular event'''

    event_id = 1
    attendees = Attendee.query.filter_by(event_id=event_id).all()

    tables = Table.query.filter_by(event_id=event_id).all()


    return render_template('event-info.html', 
                            attendees=attendees,
                            tables=tables)

@app.route('/attendee/<int:attendee_id>')
def attendee_detail(attendee_id):
    '''Show info about user.'''

    # store the attendee_id from the page
    attendee = Attendee.query.get(attendee_id)

    # query for all attendees with the same event_id
    event_id = 1
    attendees = Attendee.query.filter_by(event_id=event_id).all()

    # store the query for relationships for the attendee
    # filter by primary attendee id or secondary attendee id
    relationships = db.session.query(SeatingRelationship).filter(
        (SeatingRelationship.primary_attendee == attendee_id) | (
            SeatingRelationship.secondary_attendee == attendee_id)).all()

    # find the other relationship to the attendee
    relationships_with_attendee = []
    for r in relationships:
        relationship_attendee = None
        if r.primary_attendee == attendee_id:
            relationship_attendee = Attendee.query.get(r.secondary_attendee)
        else:
            relationship_attendee = Attendee.query.get(r.primary_attendee)

        relationships_with_attendee.append((relationship_attendee, r.relationship_code)) 



    return render_template("attendee.html", 
                            attendee=attendee, 
                            attendees=attendees, 
                            relationships_with_attendee=relationships_with_attendee)

@app.route('/attendee/<int:attendee_id>', methods=['POST'])
def update_relationship(attendee_id):
    '''update relationship of the user in the database'''

    attendee = Attendee.query.get(attendee_id)

    # get form variables
    secondary_attendee = int(request.form['secondary-attendee'])

    relationship_code = request.form['relationship-code']

    relationship = SeatingRelationship(primary_attendee=attendee_id, 
                                        secondary_attendee=secondary_attendee,
                                        relationship_code=relationship_code)
    flash('Relationship added.')
    db.session.add(relationship)
    db.session.commit()

    return redirect('/attendee/{}'.format(attendee.attendee_id))

@app.route('/create-tables', methods=['POST'])
def create_tables():
    '''create tables'''

    event_id = 1

    table_name = request.form['table-name']

    max_seats = int(request.form['max-seats'])

    table = Table(event_id=event_id,
                    table_name=table_name,
                    max_seats=max_seats)

    db.session.add(table)
    db.session.commit()

    return redirect('/event-info')

@app.route('/table-info/<int:table_id>')
def table_detail(table_id):
    '''Show info about a table.'''

    table = Table.query.get(table_id)

    return render_template('/table-info.html',
                            table=table)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
