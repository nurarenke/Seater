# Seater

<img src="/static/seater_logo.png" width="200" height="200"/>

Seater is the project of Nura Renke while a student at [Hackbright Academy](https://hackbrightacademy.com/) in San Francisco, August 2017.

# Overview & Features

Seater is a dynamic seating app for event planning that uses a sophisticated algorithm to seat your guests instantly based on their relationships.

# Tech Stack

Server: Python, Flask with Jinja templates

Database: SQL, using Postgres and SQLAlchemy

Backend/Algorithms: Python implementations of custom algorithms

Frontend: CSS, Javascript, JQuery, Bootstrap, HTML5

Testing: Unittest

# Screenshots

Homepage

<img src="/static/log_in_screen.png"/>

Homepage for a logged in user showing a list of events.

<img src="/static/events_page.png"/>

Event info page.

<img src="/static/event_info.png"/>

Attendee info and create relationships page.

<img src="/static/attendee_page.png"/>

Table assignments page.

<img src="/static/tables.png"/>

Component Files of Note

`server.py` contains the the routes accessible directly by the user, as well as those accessed asynchronously to provide data to the client.

`model.py` provides the data model associated with user interaction and database storage: Events, Attendees, Tables, Relationships, Users, etc.

`assignments.py` provides the algorithm for seating arrangement. Based on attendees, tables and relationships for a particular event, the algorithm builds clusters of attendees that all mutually have to sit with each other via the "must" relationships.The algorithm then recursively seats each cluster at the table that has both the most open seats as well as the most fulfilled optional “want” relationships with people already seated at the tables. And of course, the algorithm also checks if that table has someone that the attendee must not sit with, the algorithm will never break that rule.
