import random 

def find_random_attendee():
 # calculate how many attendees the user created
    number_of_attendees = Attendee.query.count()

    # pick a random number
    attendee_id = random.randint(1, number_of_attendees)

    # store the attendee according to the random number
    attendee = Attendee.query.get(attendee_id)

    return attendee

attendee = find_random_attendee()

def find_relationships(attendee):

    # store the relationships for that attendee
    relationships = db.session.query(SeatingRelationship).filter(
        (SeatingRelationship.primary_attendee == attendee.attendee_id) | (
            SeatingRelationship.secondary_attendee == attendee.attendee_id)).all()

    print relationships

    relationships_with_attendee = []
    for r in relationships:
        relationship_attendee = None
        if r.primary_attendee == attendee.attendee_id:
            relationship_attendee = Attendee.query.get(r.secondary_attendee)
        else:
            relationship_attendee = Attendee.query.get(r.primary_attendee)

        relationships_with_attendee.append((relationship_attendee, r.relationship_code))

    return relationships_with_attendee

relationships = find_relationships(attendee)

def table_assignments():
    # calculate how many tables the user created
    number_of_tables = Table.query.count()

    # create a dictionary of tables and max seats
    list_of_tables = {}

    tables = Table.query.all()

    for table in tables:
        list_of_tables[table.table_id] = table.max_seats

        if list_of_tables[table.table_id] > 0:


    try 
    #assign attendee to first table








# attendees = Attendee.query.all()

# relationships_list = []
# #loop through each attendee and get their seating relationships
# for attendee in attendees:
#     relationships = db.session.query(SeatingRelationship).filter(
#         (SeatingRelationship.primary_attendee == attendee.attendee_id) | (
#             SeatingRelationship.secondary_attendee == attendee.attendee_id)).all()
#     relationships_list.append(relationships)

# #loop through each relationships and only store the ones with relationships
# attendee_relationships = []
# no_relationships = []
# for r in relationships_list:
#     if not r:
#     no_relationships.append(r)
# else:
#     attendee_relationships.append(r)



# #loop through the relationships and make pairs
# must_pairs = []
# want_pairs = []
# must_not_pairs = []

# for relation in attendee_relationships:
#     if relationship_code == 'must':
#         must_pairs.append(relation)
#     elif relationship_code == 'want':
#         want_pairs.append(relation)
#     else:
#         must_not_pairs.append(relationship_code)