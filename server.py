"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Attendee, Event, Table, SeatingRelationship

from assignments import table_assignments


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

@app.route('/register', methods=['GET'])
def register_form():
    """Show form for user signup."""

    return render_template("register-form.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form['email']
    password = request.form['password']
    name = request.form['name']

    new_user = User(email=email, password=password, name=name)

    db.session.add(new_user)
    db.session.commit()

    flash("User {} added.".format(name))
    return render_template('/events.html')

@app.route('/login', methods=['GET'])
def login_form():
    '''Show login form'''

    return render_template('login-form.html')

@app.route('/login', methods=['POST'])
def login_process():
    '''Process login'''

    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/")

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")

@app.route('/events/')
def display_events():
    '''Displays user's events'''

    user_id = session.get("user_id")

    if user_id:
        user_events = Event.query.filter_by(user_id = user_id).all()

    else:
        user_events = None

    return render_template('/events.html',
                            user_events=user_events)

@app.route('/event-info/<int:event_id>')
def display_attendee_list(event_id):
    '''displays a list of attendees and tables for a particular event'''

    attendees = Attendee.query.filter_by(event_id=event_id).all()

    tables = Table.query.filter_by(event_id=event_id).all()


    return render_template('event-info.html', 
                            attendees=attendees,
                            tables=tables)

@app.route('/attendee/<int:attendee_id>/<int:event_id>')
def attendee_detail(attendee_id, event_id):
    '''Show info about user and relationships.'''

    # store the attendee_id from the page
    attendee = Attendee.query.get(attendee_id)

    # query for all attendees with the same event_id
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

    # add relationship to the database
    relationship = SeatingRelationship(primary_attendee=attendee_id, 
                                        secondary_attendee=secondary_attendee,
                                        relationship_code=relationship_code)
    flash('Relationship added.')
    db.session.add(relationship)
    db.session.commit()

    return redirect('/attendee/{}'.format(attendee.attendee_id))

@app.route('/create-tables/', methods=['POST'])
def create_tables():
    '''create tables'''

    # retrieve values from the form
    table_name = request.form['table-name']

    max_seats = int(request.form['max-seats'])

    user_id = session.get("user_id")

    event_id = db.session.query(Event.event_id).filter(Event.user_id == user_id).first()

    # add the table to the database
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

    seated_at_table = Attendee.query.filter_by(table_id=table_id).all()

    return render_template('/table-info.html',
                            table=table,
                            seated_at_table=seated_at_table)

@app.route('/table_assignments', methods=['POST'])
def assign_tables():
    '''assign tables'''

    assignments = table_assignments()

    # query for how many tables the user created
    user_id = session.get("user_id")
    event_id = db.session.query(Event.event_id).filter(Event.user_id == user_id).first()
    table_count = db.session.query(Table).filter(Table.event_id == event_id).count()
    table_numbers = range(1, (table_count + 1))

    # add attendees to the appropiate table in the database
    while table_count > 0:
        for table_number in table_numbers:
            for attendee_id in assignments[table_number]:
                attendee = db.session.query(Attendee).filter(
                    Attendee.attendee_id==attendee_id).first()
                attendee.table_id = table_number
                table_count -= 1
                db.session.add(attendee)
        
    db.session.commit()

    # query for all of attendees who are assigned to a table
    assigned_attendees = db.session.query(Attendee).filter(Attendee.table_id != None).join(
        Table).order_by(Attendee.table_id).all()


    return render_template('/table-assignments.html',
                            assigned_attendees=assigned_attendees)
 
@app.route('/assignment-info.json')
def get_assignment_info():
    '''Get delivery info'''

    assigned_attendees = db.session.query(Attendee).filter(Attendee.table_id != None).join(
        Table).order_by(Attendee.table_id).all()

    return jsonify(assigned_attendees)

@app.route('/dynamic-table-display')
def display_tables_dynamically():
    '''Display tables dynamically'''

    return render_template('/dynamic-table-display.html')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")
