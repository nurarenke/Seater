from model import connect_to_db, db, User, Attendee, Event, Table, SeatingRelationship
from server import app

# db = SQLAlchemy()
def table_assignments():
    # query for all of attendees
    # TODO: filter by event_id
    attendees = db.session.query(Attendee).all()

    relationships = build_relationships(attendees)

    clusters = build_clusters(attendees, relationships)


def build_clusters(attendees, relationships):
    ''' Builds a list of lists of attendee id clusters'''
    clusters = []

    for attendee in attendees:
        attendee_id = attendee.attendee_id
        attendee_relationships = relationships[attendee_id]
        
        # get the list of must sit withs, or an empty list if no musts
        must_attendees = []
        if 'must' in attendee_relationships:
            must_attendees = attendee_relationships['must']

        seated = False
        # check all the clusters for the the attendee or the attendee's musts
        for cluster in clusters:
            # if the attendee was already seated, stop
            if attendee_id in cluster:
                seated = True
                break

            # if the musts share an attendee with this cluster,
            # add the attendee and any unseated musts to this cluster
            if not set(cluster).isdisjoint(must_attendees):
                seated = True
                cluster.append(attendee_id)
                for must in musts:
                    if must not in cluster:
                        cluster.append(must)
                break

        # if there were no musts to sit with, none of the cluster has been 
        # seated yet, so seat the attendee and his cluster
        if not seated:
            cluster = [attendee_id]
            cluster.extend(must_attendees)
            clusters.append(cluster)

    # print out the clusters for debugging purposes
    for cluster in clusters:
        print str(cluster)

    return clusters


def build_relationships(attendees):
    ''' Builds a dictionary attendee_ids to dictionaries of relationship code to attendee id'''
    relation_dict = {}

    for attendee in attendees:

        # create dictionary of attendees with their attendee_id as the key
        attendee_relationship_dict = {}

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
            relationship_id = relationship_attendee.attendee_id

            # add the relationship_id to the set of attendee_ids for the relationship_code
            if relationship_code in attendee_relationship_dict:
                attendee_relationship_dict[relationship_code].add(relationship_id)
            else:
                attendee_relationship_dict[relationship_code] = set([relationship_id])

        # store the relationships for this attendee in the relationship_dict
        relation_dict[attendee.attendee_id] = attendee_relationship_dict

    # print out the relationships for debugging purposes
    for tup, val in relation_dict.items():
        print str(tup) + " | " + str(val)

    return relation_dict

if __name__ == "__main__":
    connect_to_db(app)
    table_assignments()