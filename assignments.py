# from flask_sqlalchemy import SQLAlchemy
# from model import User, Attendee, Event, Table, SeatingRelationship

# db = SQLAlchemy()
attendees = db.session.query(Attendee).all()
relation_dict = {}

for attendee in attendees:

    relation_dict[attendee.attendee_id] = {}
    # store the relationships for that attendee
    relationships = db.session.query(SeatingRelationship).filter(
        (SeatingRelationship.primary_attendee == attendee.attendee_id) | (
            SeatingRelationship.secondary_attendee == attendee.attendee_id)).all()

    relationship_code = []
    relationship_attendee = []
    for r in relationships:
        relationship_attendee = None
        if r.primary_attendee == attendee.attendee_id:
            relationship_attendee = Attendee.query.get(r.secondary_attendee)
        else:
            relationship_attendee = Attendee.query.get(r.primary_attendee)

        relationship_code = r.relationship_code
        relationships_attendee = relationships_attendee

    relation_dict[attendee.attendee_id][relationship_code]=relationship_attendee

print relation_dict

