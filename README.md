# Seater

<img src="/static/seater_logo.png" width="200" height="200"/>

Seater is the project of Nura Renke while a student at [Hackbright Academy](https://hackbrightacademy.com/) in San Francisco, August 2017.

# Overview & Features

Seater is a dynamic seating app for event planning that uses a sophisticated algorithm to seat your guests instantly based on their relationships. My motivation for the project comes from my background in event planning. One of the challenges of planning any type of event is the seating chart. I wanted to make it easier on the user and create those seating arrangments based on relationships, the number of tables, and the number of attendees.

There are three types of relationships between attendees: "must sit with", "want to sit with", and "must not sit with". The "must sit with" relationships take priority, while the "want to sit with" are optional. However, there are a few "must not sit withs" at every event and those cannot be broken in order to have a succesful event. 

The user can also create and edit any number of attendees and tables. A user can also have multiple events, which hold all of the attendees, tables, relationships, and table assignments for each indiviudal event.

## Tech Stack

Server: Python, Flask with Jinja templates

Database: SQL, using Postgres and SQLAlchemy

Backend/Algorithms: Python implementations of custom algorithms

Frontend: CSS, Javascript, JQuery, Bootstrap, HTML5

Testing: Unittest

## Screenshots

Homepage

<img src="/static/log_in_screen.png"/>

Homepage for a logged in user showing a list of events.

<img src="/static/events_page.png"/>

Event info page.

<img src="/static/event_info_page.png"/>

Attendee info and create relationships page.

<img src="/static/attendee_page.png"/>

Table assignments page.

<img src="/static/tables.png"/>

## Component Files of Note

`server.py` contains the the routes accessible directly by the user, as well as those accessed asynchronously to provide data to the client.

`model.py` provides the data model associated with user interaction and database storage: Events, Attendees, Tables, Relationships, Users, etc.

`assignments.py` provides the algorithm for seating arrangement. Based on attendees, tables and relationships for a particular event, the algorithm builds clusters of attendees that all mutually have to sit with each other via the "must" relationships.The algorithm then recursively seats each cluster at the table that has both the most open seats as well as the most fulfilled optional “want” relationships with people already seated at the tables. And of course, the algorithm also checks if that table has someone that the attendee must not sit with, the algorithm will never break that rule.
