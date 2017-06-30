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

    fake_users = [("nura@gmail.com", "password", fake.name()),
    ("burger@gmail.com", "password", fake.name()),
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


if __name__ == "__main__":
    connect_to_db(app)

# add fake users to database
store_users()

# grab the first user 
event_owner = User.query.first()

# delete any previous events
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

   
    
   
