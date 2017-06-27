"""Utility file to seed seater database from faker data"""

import datetime
from sqlalchemy import func

from model import User, Attendee, Event, Table, EventAttendeeSeat, SeatingRelationship, connect_to_db, db
from server import app

from faker import Factory

# using a python faker package to generate fake data for the database
fake = Factory.create()

def create_fake_users(howmany):
    '''autogenerate fake users'''

    user_data = []
    
    for _ in range(0, howmany):
        user_data.append((fake.first_name(), fake.last_name()))
    return user_data

fake_users = create_fake_users(50)

def load_users():
    """Load users from fake_users into database."""

    print "Users"
     
    for first_name, last_name in fake_users:

        user = User(user_id=user_id,
                    first_name=first_name,
                    last_name=last_name)

        # We need to add to the session 
        db.session.add(user)

        # provide some sense of progress
        if i % 100 == 0:
            print i

    # Once we're done, we commit our work
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app)
    db.create_all()

    load_users()
   

    db.session.commit()
    
   
