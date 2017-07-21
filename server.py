"""Seater."""

from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt

from model import connect_to_db, db, User, Attendee, Event, Table, SeatingRelationship

from assignments import table_assignments


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "Lava12#$!!"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload = True

@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


@app.route('/register', methods=['POST'])
def register_process():
    """Process registration."""

    # Get form variables
    email = request.form.get('email')
    password = request.form.get('password').dec
    name = request.form.get('name')

    # Check to see if the user is already registered
    if db.session.query(User).filter(User.email == email).all():
        flash('You are already registered with that email')
        return redirect('/')

    # Create a hash of the user's password
    pw_hash = bcrypt.generate_password_hash(password)

    # If it's a new email, add the user to the database
    new_user = User(email=email, password=pw_hash, name=name)
    db.session.add(new_user)
    db.session.commit()

    # Save the user id in a session
    session["user_id"] = new_user.user_id

    flash("Welcome {}".format(name))
    return redirect('/events')


@app.route('/login', methods=['POST'])
def login_process():
    '''Process login'''

    # Get form variables
    email = request.form.get("email")
    password = request.form.get("password")

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/")

    if not bcrypt.check_password_hash(user.password, password):

        flash("Incorrect password")
        return redirect("/")

    session["user_id"] = user.user_id

    flash("Logged in")
    return redirect("/events")

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")

@app.route('/events', methods=['GET'])
def display_events():
    '''Displays user's events'''
    if is_not_logged_in():
        return redirect('/')

    # grab the user_id
    user_id = session.get("user_id")

    # query for events based on the user_id
    if user_id:
        user_events = Event.query.filter_by(user_id = user_id).all()

    else:
        user_events = None

    return render_template('/events.html',
                            user_events=user_events)

@app.route('/events', methods=['POST'])
def add_event():
    '''Update the database with new event'''
    if is_not_logged_in():
        return redirect('/')

    # grab the user_id from the session
    user_id = session.get("user_id")

    # get form values
    event_name = request.form.get('event_name')
    event_description = request.form.get('event_description')
    location = request.form.get('location')
    time = request.form.get('time')

    # insert new event into database
    new_event = Event(event_name=event_name,
                    event_description=event_description,
                    location=location,
                    time=time,
                    user_id=user_id)

    flash('Event added.')
    db.session.add(new_event)
    db.session.commit()

    return redirect('/event-info/{}'.format(new_event.event_id))

@app.route('/event=<int:event_id>/update-event', methods=['GET'])
def display_edit_event(event_id):
    '''Display edit event form'''
    if is_not_logged_in():
        return redirect('/')

    event = Event.query.filter_by(event_id=event_id).first()
    return render_template('edit-event.html',
                            event=event)

@app.route('/event=<int:event_id>/update-event', methods=['POST'])
def update_event(event_id):

    # get form values
    event_name = request.form.get('event_name')
    event_description = request.form.get('event_description')
    location = request.form.get('location')
    time = request.form.get('time')

    updated_event = Event.query.filter_by(event_id=event_id).first()

    updated_event.event_name = event_name
    updated_event.event_description = event_description
    updated_event.location = location
    updated_event.time = time

    db.session.add(updated_event)
    db.session.commit()

    return redirect('/event={}/event-info'.format(event_id))

@app.route('/event=<int:event_id>/delete-event', methods=['POST'])
def delete_event(event_id):

    
    deleted_attendees = Attendee.query.filter_by(event_id=event_id).all()
    for attendee in deleted_attendees:
        relationships = db.session.query(SeatingRelationship).filter(
            (SeatingRelationship.primary_attendee == attendee.attendee_id) | (
                SeatingRelationship.secondary_attendee == attendee.attendee_id)).all()

        for relationship in relationships:
            db.session.delete(relationship)

        db.session.delete(attendee)


    deleted_tables = Table.query.filter_by(event_id=event_id).all()
    for table in deleted_tables:
        db.session.delete(table)

    deleted_event = Event.query.filter_by(event_id=event_id).first()
    db.session.delete(deleted_event)

    flash('{} has been removed'.format(deleted_event.event_name))
    db.session.commit()

    return redirect('/events')

    
@app.route('/event=<int:event_id>/event-info/')
def display_event_info(event_id):
    '''displays a list of attendees and tables for a particular event'''
    if is_not_logged_in():
        return redirect('/')

    event = Event.query.get(event_id)

    attendees = Attendee.query.filter_by(event_id=event_id).all()

    tables = Table.query.filter_by(event_id=event_id).all()


    return render_template('event-info.html', 
                            event=event,
                            attendees=attendees,
                            tables=tables)

@app.route('/create-attendee/<int:event_id>', methods=['POST'])
def create_attendee(event_id):
    '''Create an attendee in the database'''
    if is_not_logged_in():
        return redirect('/')

    # get form values
    first_name = request.form.get('first_name') 
    last_name = request.form.get('last_name') 
    email = request.form.get('email')
    street = request.form.get('street') 
    city = request.form.get('city')
    state = request.form.get('state') 
    zipcode = request.form.get('zipcode') 
    meal_request = request.form.get('meal_request') 
    note = request.form.get('note')
    is_vip = request.form.get('vip') == 'True'

    user_id = session.get("user_id")
   
    # update the database
    new_attendee = Attendee(first_name=first_name,
                            last_name=last_name,
                            attendee_email=email,
                            street=street,
                            city=city,
                            state=state,
                            zipcode=zipcode,
                            is_vip=is_vip,
                            meal_request=meal_request,
                            note=note,
                            event_id=event_id)
    flash('Attendee added.')
    db.session.add(new_attendee)
    db.session.commit()
   
    return redirect('/attendee/{}/{}'.format(
                    new_attendee.event_id,
                    new_attendee.attendee_id))

@app.route('/attendee/<int:event_id>/new-attendee')
def new_attendee(event_id):
    '''Shows an empty attendee info page for filling out to make a new attendee.'''
    if is_not_logged_in():
        return redirect('/')

    attendee = None
    event_id = event_id

    return render_template("attendee.html",
                            attendee=attendee,
                            event_id=event_id)

@app.route('/<int:event_id>/delete-attendee/<int:attendee_id>', methods=['POST'])
def delete_attendee(event_id, attendee_id):
    if is_not_logged_in():
        return redirect('/')

    delete_attendee = Attendee.query.filter_by(attendee_id = attendee_id).first()

    relationships = db.session.query(SeatingRelationship).filter(
            (SeatingRelationship.primary_attendee == attendee_id) | (
                SeatingRelationship.secondary_attendee == attendee_id)).all()

    for relationship in relationships:
        db.session.delete(relationship)

    flash('{} {} has been removed'.format(delete_attendee.first_name,
                                        delete_attendee.last_name))
    
    db.session.delete(delete_attendee)
    db.session.commit()

    return redirect('/event={}/event-info'.format(event_id))

@app.route('/<int:event_id>/update-attendee/<int:attendee_id>', methods=['POST'])
def update_attendee(event_id, attendee_id):
    if is_not_logged_in():
        return redirect('/')

    first_name = request.form.get('first_name') 
    last_name = request.form.get('last_name') 
    email = request.form.get('email')
    street = request.form.get('street') 
    city = request.form.get('city')
    state = request.form.get('state') 
    zipcode = request.form.get('zipcode') 
    meal_request = request.form.get('meal_request') 
    note = request.form.get('note')
    is_vip = request.form.get('vip') == 'True'

    updated_attendee = db.session.query(Attendee).filter(
        Attendee.attendee_id==attendee_id).first()

    updated_attendee.first_name = first_name
    updated_attendee.last_name = last_name
    updated_attendee.email = email
    updated_attendee.street = street
    updated_attendee.city = city
    updated_attendee.state = state
    updated_attendee.zipcode = zipcode
    updated_attendee.meal_request = meal_request
    updated_attendee.note = note
    updated_attendee.is_vip = is_vip

    db.session.add(updated_attendee)
    db.session.commit()
    
    return redirect('/attendee/{}/{}'.format(event_id, attendee_id))

@app.route('/attendee/<int:event_id>/<int:attendee_id>')
def display_attendee(event_id, attendee_id):
    '''Show info about user and relationships.'''
    if is_not_logged_in():
        return redirect('/')

    event_id = event_id
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
    relationships_attendee_ids = []
    for r in relationships:
        relationship_attendee = None
        if r.primary_attendee == attendee_id:
            relationship_attendee = Attendee.query.get(r.secondary_attendee)
        else:
            relationship_attendee = Attendee.query.get(r.primary_attendee)
        
        relationships_attendee_ids.append(relationship_attendee.attendee_id)
        relationships_with_attendee.append((relationship_attendee, r.relationship_code)) 

    # look for attendees with no relationships
    attendees_not_yet_related_to = []
    for a in attendees:
            if a.attendee_id not in relationships_attendee_ids and a.attendee_id != attendee_id:
                attendees_not_yet_related_to.append(a)

    return render_template("attendee.html", 
                            attendee=attendee, 
                            attendees=attendees,
                            event_id=event_id, 
                            relationships_with_attendee=relationships_with_attendee,
                            attendees_not_yet_related_to=attendees_not_yet_related_to)

@app.route('/event=<int:event_id>/delete-attendee/<int:attendee_id>/<int:secondary_attendee_id>', methods=['POST'])
def delete_relationship(attendee_id, secondary_attendee_id, event_id):

    event_id = event_id
    current_attendee_relationship = db.session.query(SeatingRelationship).filter(
        (
            (SeatingRelationship.primary_attendee == attendee_id) &
            (SeatingRelationship.secondary_attendee == secondary_attendee_id)
        ) | 
        (
            (SeatingRelationship.primary_attendee == secondary_attendee_id) &
            (SeatingRelationship.secondary_attendee == attendee_id)
        )
    ).first()

    flash('Relationship deleted')
    db.session.delete(current_attendee_relationship)
    db.session.commit()

    return redirect('/attendee/{}/{}'.format(event_id, attendee_id))

@app.route('/attendee/<int:attendee_id>/<int:event_id>', methods=['POST'])
def update_relationship(attendee_id, event_id):
    '''update relationship of the user in the database'''
    if is_not_logged_in():
        return redirect('/')

    event_id = event_id

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

    return redirect('/attendee/{}/{}'.format(event_id, attendee.attendee_id,
                    attendee_id=attendee_id,
                    event_id=event_id))

@app.route('/event=<int:event_id>/new-table/', methods=['GET'])
def new_table(event_id):
    table = None
    event_id = event_id
    seated_at_table = None

    return render_template('table-info.html',
                            event_id=event_id,
                            seated_at_table=seated_at_table,
                            table=table)

@app.route('/event=<int:event_id>/create-tables/', methods=['POST'])
def create_tables(event_id):
    '''create tables'''
    if is_not_logged_in():
        return redirect('/')

    # retrieve values from the form
    table_name = request.form['table-name']

    max_seats = int(request.form['max-seats'])

    event_id = event_id

    # add the table to the database
    table = Table(event_id=event_id,
                    table_name=table_name,
                    max_seats=max_seats)

    db.session.add(table)
    db.session.commit()

    return redirect('/event={}/event-info'.format(event_id))

@app.route('/event=<int:event_id>/update-table/table=<int:table_id>', methods=['POST'])
def update_table(event_id, table_id):
    
    if is_not_logged_in():
        return redirect('/')

    # retrieve values from the form
    table_name = request.form['table-name']

    max_seats = int(request.form['max-seats'])

    event_id = event_id

    updated_table = Table.query.filter_by(table_id=table_id).first()

    # update the table in the database
    updated_table.event_id=event_id
    updated_table.table_name=table_name
    updated_table.max_seats=max_seats

    db.session.add(updated_table)
    db.session.commit()

    return redirect('/event={}/table-info/{}'.format(event_id, table_id))

@app.route('/event=<int:event_id>/delete-table/table=<int:table_id>', methods=['POST'])
def delete_table(event_id, table_id):
    '''delete table'''

    table_to_delete = Table.query.filter_by(table_id=table_id).first()

    table_assignments_to_delete = Attendee.query.filter_by(table_id=table_id).all()

    # replace table assignments with none for each attendee at that table
    for attendee in table_assignments_to_delete:
        attendee.table_id = None

    db.session.delete(table_to_delete)
    db.session.commit()

    return redirect('/event={}/event-info'.format(event_id))

@app.route('/event=<int:event_id>/table-info/<int:table_id>')
def table_detail(event_id, table_id):
    '''Show info about a table.'''
    if is_not_logged_in():
        return redirect('/')

    event_id = event_id

    table = Table.query.get(table_id)

    seated_at_table = Attendee.query.filter_by(table_id=table_id).all()

    return render_template('/table-info.html',
                            table=table,
                            seated_at_table=seated_at_table,
                            event_id=event_id)

@app.route('/event=<int:event_id>/table-assignments/', methods=['POST'])
def assign_tables(event_id):
    '''assign tables'''
    if is_not_logged_in():
        return redirect('/')

    attendee_ids = []
    for attendee in db.session.query(Attendee).filter(Attendee.event_id == event_id).all():
        attendee_ids.append(attendee.attendee_id)

    table_ids = {}
    total_seats = 0;
    for table in db.session.query(Table).filter(Table.event_id == event_id).all():
        table_ids[table.table_id] = table.max_seats
        total_seats += table.max_seats

    assignments = table_assignments(event_id, attendee_ids, table_ids, total_seats)
    # check if assignments None
    if not assignments:
        flash("Could not build a valid seating assignment.")
        return redirect('/event={}/table-assignments/'.format(event_id))
   
    # add attendees to the appropiate table in the database

    for table_id, attendee_ids in assignments.items():
        for attendee_id in attendee_ids:
            attendee = db.session.query(Attendee).filter(
                Attendee.attendee_id==attendee_id).first()
            attendee.table_id = table_id
            db.session.add(attendee)
        
    db.session.commit()
    return redirect('/event={}/table-assignments/'.format(event_id))

@app.route('/event=<int:event_id>/table-assignments/', methods=['GET'])
def display_tables(event_id):
    '''display tables'''
    if is_not_logged_in():
        return redirect('/')

    event_id=event_id
    # query for all of attendees who are assigned to a table
    assigned_attendees = db.session.query(Attendee).filter(Attendee.event_id == event_id, Attendee.table_id != None).join(
        Table).order_by(Table.table_name).all()

    assigned_tables = db.session.query(Table).filter(Table.event_id == event_id).order_by(Table.table_name).all()

    return render_template('/table-assignments.html',
                            assigned_attendees=assigned_attendees,
                            assigned_tables=assigned_tables,
                            event_id=event_id)

@app.route('/event=<int:event_id>/clear-table-assignments/', methods=['POST'])
def clear_tables(event_id):
    if is_not_logged_in():
        return redirect('/')

    event_id=event_id

     # query for all of attendees who are assigned to a table
    assigned_attendees = db.session.query(Attendee).filter(Attendee.event_id == event_id, Attendee.table_id != None).join(
        Table).order_by(Table.table_name).all()

    for a in assigned_attendees:
        a.table_id = None
        db.session.add(a)
        db.session.commit()

    return redirect(('/event={}/table-assignments/').format(event_id))


def is_not_logged_in():
    if not session.get('user_id'):
        flash('You are currently not logged in')
        return True
    return False
 

@app.route('/dynamic-table-display')
def display_tables_dynamically():
    '''Display tables dynamically'''
    is_not_logged_in()

    return render_template('/dynamic-table-display.html')
        


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    bcrypt = Bcrypt(app)

    app.run(host="0.0.0.0")
