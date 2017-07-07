from model import connect_to_db, db, User, Attendee, Event, Table, SeatingRelationship
from server import app

# db = SQLAlchemy()
def table_assignments():
    # query for all of attendees
    # TODO: filter by event_id
    attendees = []
    for attendee in db.session.query(Attendee).all():
        attendees.append(attendee.attendee_id)
    
    # TODO: filter by event_id
    tables = {}
    total_seats = 0;
    for table in db.session.query(Table).all():
        tables[table.table_id] = table.max_seats
        total_seats += table.max_seats

    # dont even try to solve this if there isnt enough seats
    if (total_seats < len(attendees)):
        print "Not enough seats! {} attendees but only {} seats!".format(str(len(attendees)), str(total_seats))
        return False

    relationships = build_relationships(attendees)

    clusters = build_clusters(attendees, relationships)

    assignments = assign_seats(clusters, relationships, tables)

    if not assignments:
        print "No valid seating could be made. :("
        return None
    else:
        # debugging
        for table_id, seated_attendees in assignments.items():
            print str(table_id) + " | " + str(seated_attendees)

        return assignments

def assign_seats(clusters, relationships, tables):
    '''Put the attendees at tables based on their relationships'''
    assignments = {}
    
    # sort the clusters by size so we seat the biggest ones first
    sorted_clusters = sorted(clusters, key=lambda cluster: -len(cluster))

    # debugging    
    print "unsorted: " + str(clusters)
    print "sorted:   " + str(sorted_clusters)

    success = assign_seats_recursive(assignments, sorted_clusters, relationships, tables)

    if success:
        return assignments
    else:
        return None


def assign_seats_recursive(assignments, sorted_clusters, relationships, tables):
    ''' Attempt to seat a cluster at a table'''

    if len(sorted_clusters) == 0:
        return True

    cluster = sorted_clusters[0]
    cluster_size = len(cluster)
    must_not_attendees = set()
    want_attendees = set()

    for attendee_id in cluster:
        if 'must_not' in relationships[attendee_id]:
            must_not_attendees.update(relationships[attendee_id]['must_not'])
        if 'want' in relationships[attendee_id]:
            want_attendees.update(relationships[attendee_id]['want'])

    attempted_tables = set()

    while True:
        table_id = get_table_id_to_attempt(tables, cluster_size, attempted_tables, must_not_attendees, want_attendees, assignments)
       
        print "{} trying table {}...".format(str(attendee_id), str(table_id))

        if not table_id:
            print "No table found for " + str(cluster) + ", returning False"
            return False

        if table_id not in assignments:
            assignments[table_id] = []

        print "BEFORE: " + str(assignments[table_id])
        
        # seat the cluster at the table and mark that we tried that table
        assignments[table_id].extend(cluster)
        attempted_tables.add(table_id)

        print "AFTER:  " + str(assignments[table_id])

        # continue trying to seat the reamining clusters
        success = assign_seats_recursive(assignments, sorted_clusters[1:], relationships, tables)

        if not success:
            # if the seating attempt was unsuccessful after the recursion, unseat this cluster
            # by unassigning each attendee from the cluster that was seated at the table we tried
            for attendee_id in cluster:
                assignments[table_id].remove(attendee_id)

            print "Recursion failed, unseating cluster {} for table {}".format(str(cluster), str(table_id))
        else:
            print "Success for cluster {} for table {}".format(str(cluster), str(table_id))
            return True


def count_wants(table, assignments, want_attendees):
    ''' Counts the number of wanted attendees currently seated at the table'''
    wants = 0
    seated_attendees = assignments.get(table, [])
    for want_attendee in want_attendees:
        if want_attendee in seated_attendees:
            wants += 1
    return wants


def get_table_id_to_attempt(tables, cluster_size, attempted_tables, must_not_attendees, want_attendees, assignments):
    ''' Gets a table that:
        -doesn't have anyone sitting at it that must not be sat with
        -has enough space
        -hasn't been tried
        -priorities the table with the most people we want to sit with
    '''
    # sort the tables so the biggest ones are first
    sorted_tables = sorted(tables.keys(), key=lambda table: -(tables[table] - len(assignments.get(table, []))))

    # sort the tables so the ones with the most wants at them are first
    # using a function in a lambda is cool
    # https://stackoverflow.com/questions/134626/which-is-more-preferable-to-use-in-python-lambda-functions-or-nested-functions
    sorted_tables = sorted(sorted_tables, key=lambda table: -count_wants(table, assignments, want_attendees))

    print "tables unsorted: " + str(tables.values())
    print "tables sorted:   " + str(sorted_tables)

    for table in sorted_tables:

        # if there are enough seats at this table, skip it
        if tables[table] - len(assignments.get(table, [])) < cluster_size:
            continue

        # if we've already tried this table, skip it
        if table in attempted_tables:
            continue

        # if we hate someone who is there, skip it
        if not must_not_attendees.isdisjoint(assignments.get(table, [])):
            continue

        return table

    return None



def build_clusters(attendees, relationships):
    '''Builds a list of lists of attendee id clusters'''
    clusters = []

    for attendee_id in attendees:
        attendee_relationships = relationships[attendee_id]
        
        # get the list of must sit withs, or an empty list if no musts
        must_attendees = []
        if 'must' in attendee_relationships:
            must_attendees = attendee_relationships['must']

        in_a_cluster = False
        # check all the clusters for the attendee or the attendee's musts
        for cluster in clusters:
            # if the attendee was already in a cluster, stop
            if attendee_id in cluster:
                in_a_cluster = True
                break

            # if the musts share an attendee with this cluster, add the attendee
            # testing it two lists share an item
            # https://stackoverflow.com/questions/3170055/test-if-lists-share-any-items-in-python
            if not set(cluster).isdisjoint(must_attendees):
                cluster.append(attendee_id)
                in_a_cluster = True

                # loop through the must_attendees list and if the must_attendee
                # is not in the cluster, add them.
                for must_attendee in must_attendees:
                    if must_attendee not in cluster:
                        cluster.append(must_attendee)
                break

        # if there were no musts to sit, with then none of the musts were clustered yet,
        # so seat the attendee and his musts
        if not in_a_cluster:
            cluster = [attendee_id]
            cluster.extend(must_attendees)
            clusters.append(cluster)

    # print out the clusters for debugging
    for cluster in clusters:
        print str(cluster)

    return clusters


def build_relationships(attendees):
    ''' Builds a dictionary attendee_ids to dictionaries of relationship code to attendee id'''
    relation_dict = {}

    for attendee_id in attendees:

        # create dictionary of attendees with their attendee_id as the key
        attendee_relationship_dict = {}

        # store the relationships for that attendee
        # both primary attendee and secondary attendee are considered
        relationships = db.session.query(SeatingRelationship).filter(
            (SeatingRelationship.primary_attendee == attendee_id) | (
                SeatingRelationship.secondary_attendee == attendee_id)).all()

        # iterate through their relationships
        for r in relationships:
            relationship_code = None
            relationship_attendee = None
            if r.primary_attendee == attendee_id:
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
        relation_dict[attendee_id] = attendee_relationship_dict

    # print out the relationships for debugging
    for tup, val in relation_dict.items():
        print str(tup) + " | " + str(val)

    return relation_dict


if __name__ == "__main__":
    connect_to_db(app)
    table_assignments()
