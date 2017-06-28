"""Utility file to seed seater database from faker data"""

import datetime
from sqlalchemy import func

from model import User, Attendee, Event, Table, EventAttendeeSeat, SeatingRelationship, connect_to_db, db
from server import app

from faker import Factory
from random import choice

# using a python faker package to generate fake data for the database
fake = Factory.create()

def create_fake_users(howmany):
    '''autogenerate fake users'''

    user_data = []

    for _ in range(0, howmany):
        user_data.append((fake.username(), fake.email(), fake.password()))
    return user_data

def load_users():
    """Load users from fake_users into database."""

    # delete any previous users
    User.query.delete()

    fake_users = create_fake_users(50)

    print "Users"
     
    for username, email, password in fake_users:

        user = User(user_id=user_id,
                    username=username,
                    email=email,
                    password=password)

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

#TODO: find a way to create a random generation of meals
def create_fake_meal_request():
    '''random meal choice'''
    meals = ['regular', 'vegetarian', 'gluten-free', 'vegan', 'dairy-free']

    return choice(meals)

def load_attendees():
'''loads the fake attendees into the database'''
    Attendee.query.delete()

    print "Attendees"

    fake_attendees = create_fake_attendees(50)
    meal_request = create_fake_meal_request()

    for first_name, last_name, attendee_email, street, city, state, zipcode, vip_status, note in fake_attendees:

        attendee = Attendee(attendee_id=attendee_id,first_name=first_name,
                    last_name=last_name, attendee_email=attendee_email,
                    street=street, city=city,
                    state=state, zipcode=zipcode,
                    vip_status=vip_status, meal_request=meal_request, note=note)

        # We need to add to the session 
        db.session.add(attendee)

    # Once we're done, we commit our work
    db.session.commit()

def load_events():
    #TODO: finish loading events


if __name__ == "__main__":
    connect_to_db(app)

    load_users()
    load_attendees()
   
    
   
