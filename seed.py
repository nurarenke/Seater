"""Utility file to seed seater database from faker data"""

import datetime
from sqlalchemy import func

from model import User, Attendee, Event, Table, SeatingRelationship, connect_to_db, db
from server import app

from faker import Factory
from random import choice

# using a python faker package to generate fake data for the database
fake = Factory.create()

def store_users():
    """Load users from fake_users into database."""

    # delete any previous users
    User.query.delete()

    fake_users = [("nura@gmail.com", "password", 'Nura Renke'),
    ("burger@gmail.com", "password", 'Christopher'),
    ("chris@gmail.com", "password", fake.name()),
    ("ticket@gmail.com", "password", fake.name()),
    ("erby@gmail.com", "password", fake.name())]
    print fake_users
     
    for email, password, name in fake_users: 
        user = User(email=email,
                    password=password,
                    name=name)

        # We need to add to the session 
        db.session.add(user)

    # Once we're done, we commit our work
    db.session.commit()

def create_fake_attendees(howmany):
    '''autogenerate fake attendees'''

    attendee_data = []

    for _ in range(0, howmany):
        attendee_data.append((fake.first_name(), fake.last_name(), fake.email(), 
            fake.street_address(), fake.city(), fake.state_abbr(), fake.zipcode(),
            fake.boolean(),fake.sentence(nb_words=6, variable_nb_words=True, ext_word_list=None)))

    return attendee_data


def store_attendees(event):
    '''loads the fake attendees into the database'''

    Attendee.query.delete()

    print "Attendees"

    fake_attendees = create_fake_attendees(50)

    # using the lambda function, it should assign a random meal everytime 
    # you call it for each attendee
    meal_request = lambda: choice(['regular', 'regular', 'regular', 'regular', 'regular', 'regular', 'vegetarian', 'gluten-free', 'vegan', 'dairy-free'])

    for first_name, last_name, attendee_email, street, city, state, zipcode, is_vip, note in fake_attendees:

        attendee = Attendee(first_name=first_name,
                    last_name=last_name, 
                    attendee_email=attendee_email,
                    street=street, 
                    city=city, 
                    state=state, 
                    zipcode=zipcode,
                    is_vip=is_vip,
                    meal_request=meal_request(), 
                    note=note)

        # taking the passed argument of our gala dinner and adding it to each attendee
        attendee.event = event

def create_example_data():

    # add fake users to database
    store_users()

    # grab the first user 
    event_owner = User.query.first()

    # add a fake event to the database
    gala_dinner = Event(event_name='Gala Dinner',
                        event_description='Fundraiser', 
                        location='Four Seasons')

    # match the user id to the event
    gala_dinner.user_id = event_owner.user_id

    # add attendees to the event
    store_attendees(gala_dinner)

    # commit our changes and add the event
    db.session.add(gala_dinner)
    db.session.commit()

    t_one = Table(table_name='Test Table', max_seats=10, event_id=gala_dinner.event_id)
    t_two = Table(table_name='Test Table Two', max_seats=10, event_id=gala_dinner.event_id)
    t_three = Table(table_name='Test Table Three', max_seats=10, event_id=gala_dinner.event_id)
    t_four = Table(table_name='Test Table Four', max_seats=10, event_id=gala_dinner.event_id)
    t_five = Table(table_name='Test Table Five', max_seats=10, event_id=gala_dinner.event_id)

    db.session.add_all([t_one, t_two, t_three, t_four, t_five])
    db.session.commit() 

    r_one = SeatingRelationship(primary_attendee=1,
     secondary_attendee=2, 
     relationship_code='must')
    db.session.add(r_one)
    db.session.commit()

    r_two = SeatingRelationship(primary_attendee=3,
     secondary_attendee=4, 
     relationship_code='must')
    db.session.add(r_two)
    db.session.commit()

    r_three = SeatingRelationship(primary_attendee=5,
     secondary_attendee=6, 
     relationship_code='must')
    db.session.add(r_three)
    db.session.commit()

    r_four = SeatingRelationship(primary_attendee=8,
     secondary_attendee=9, 
     relationship_code='must')
    db.session.add(r_four)
    db.session.commit()

    r_five = SeatingRelationship(primary_attendee=6,
     secondary_attendee=7, 
     relationship_code='must_not')
    db.session.add(r_five)
    db.session.commit()

    r_six = SeatingRelationship(primary_attendee=7,
     secondary_attendee=4, 
     relationship_code='want')
    db.session.add(r_six)
    db.session.commit()

    # import pdb; pdb.set_trace()



if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    store_users()

    # Grab the first user
    event_owner = User.query.first()

    # Delete any previous events
    Event.query.delete()

    # add a fake event to the database
    gala_dinner = Event(event_name='Gala Dinner',
                        event_description='Fundraiser', 
                        location='Four Seasons')

    # match the user id to the event
    gala_dinner.user = event_owner

    # add attendees to the event
    store_attendees(gala_dinner)

    # commit our changes and add the event
    db.session.add(gala_dinner)
    db.session.commit()



    
   
    
   
