from model import connect_to_db, db, User, Attendee, Event, Table, SeatingRelationship
from server import app

# db = SQLAlchemy()
def table_assignments():
    # query for all of attendees
    # TODO: filter by event_id
    attendees = db.session.query(Attendee).all()
    relation_dict = {}

    for attendee in attendees:

        # create dictionary of attendees with their attendee_id as the key
        relation_dict[attendee.attendee_id] = {}

        # store the relationships for that attendee
        # both primary attendee and secondary attendee are considered
        relationships = db.session.query(SeatingRelationship).filter(
            (SeatingRelationship.primary_attendee == attendee.attendee_id) | (
                SeatingRelationship.secondary_attendee == attendee.attendee_id)).all()

        # iterate through their relationships
        for r in relationships:
            relationship_code = None
            relationship_attendee = None
            if r.primary_attendee == attendee.attendee_id:
                relationship_attendee = Attendee.query.get(r.secondary_attendee)
            else:
                relationship_attendee = Attendee.query.get(r.primary_attendee)

            relationship_code = r.relationship_code

            # create a nested dictionary of the attendee_id as the key and the value is a 
            # dictionary of relationship key to attendee_id
            relation_dict[attendee.attendee_id][relationship_code]=set(relationship_attendee.attendee_id)
            relation_dict[attendee.attendee_id][relationship_code].add(attendee.attendee_id)


    # # loop through the list of attendee ids and build sets of relationships
    # relationships_must = set()
    # for a_id, code in relation_dict.items():
    #     if 'must' in code.keys():
    #         for code, a_id_two in code.items():
    #             print code
    #             relationships_must.add(code.items()) 
    #         print relationships_must
    #     # relationships_want = set()
    #     # relationships_must_not = set()


if __name__ == "__main__":
    connect_to_db(app)
    table_assignments()