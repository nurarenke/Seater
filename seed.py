"""Utility file to seed seater database from faker data"""

import datetime
from sqlalchemy import func

from model import User, Attendee, Event, Table, SeatingRelationship, connect_to_db, db
from server import app

from faker import Factory
from random import choice

# using a python faker package to generate fake data for the database
fake = Factory.create()

def create_fake_users(howmany):
    '''autogenerate fake users'''

    user_data = []

    for _ in range(0, howmany):
        user_data.append((fake.user_name(), fake.email(), fake.password()))

    return user_data

def store_users():
    """Load users from fake_users into database."""

    # delete any previous users
    User.query.delete()

    fake_users = create_fake_users(5)
    print fake_users

    print "Users"
     
    for user_tuples in fake_users: 
        print user_tuples
        username, email, password = user_tuples
        print password

        user = User(username=username,
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


def store_attendees(event):
    '''loads the fake attendees into the database'''

    Attendee.query.delete()

    print "Attendees"

    fake_attendees = create_fake_attendees(50)

    # using the lambda function, it should assign a random meal everytime 
    # you call it for each attendee
    meal_request = lambda: choice(['regular', 'regular', 'regular', 'regular', 'regular', 'regular', 'vegetarian', 'gluten-free', 'vegan', 'dairy-free'])

    for attendee_tuples in fake_attendees:
        first_name, last_name, attendee_email, street, city, state, zipcode, vip_status, note = attendee_tuples

        attendee = Attendee(first_name=first_name,
                    last_name=last_name, 
                    attendee_email=attendee_email,
                    street=street, 
                    city=city, 
                    state=state, 
                    zipcode=zipcode,
                    vip_status=vip_status,
                    meal_request=meal_request(), 
                    note=note, 
                    # event_id=event_id,
                    table_id=None)

        attendee.event = event
        # event.attendees.append(attendee)

    #     # We need to add to the session 
    #     db.session.add(attendee)

    # # Once we're done, we commit our work
    # db.session.commit()

if __name__ == "__main__":
    connect_to_db(app)
#create users
#get a list of the users
#for each user
#  create an event
#  create the attendees for the event

store_users()
event_owner = User.query.first()

Event.query.delete()

gala_dinner = Event(event_name='Gala Dinner',
                    event_description='Fundraiser', 
                    location='Four Seasons')

gala_dinner.user = event_owner


# gala_event_query = db.session.query(Event).filter(Event.event_name=='Gala Dinner').one()
# event_id = gala_event_query.event_id

# user_query = db.session.query(User).filter(User.user_id==1).one()
# user_id = user_query.user_id

store_attendees(gala_dinner)

db.session.add(gala_dinner)
db.session.commit()

   
    
   
