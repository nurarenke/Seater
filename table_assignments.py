def find_relationships():
 # calculate how many attendees the user created
    number_of_attendees = Attendee.query.count()

# store all the attendees
    attendees = Attendee.query.all()

    while number_of_attendees >= 0:
# iterate through each attendee 
        for attendee in attendees:

            # store the relationships for that attendee
            relationships = db.session.query(SeatingRelationship).filter(
                (SeatingRelationship.primary_attendee == attendee.attendee_id) | (
                    SeatingRelationship.secondary_attendee == attendee.attendee_id)).all()

            relationships_with_attendee = []
            for r in relationships:
                relationship_attendee = None
                if r.primary_attendee == attendee.attendee_id:
                    relationship_attendee = Attendee.query.get(r.secondary_attendee)
                else:
                    relationship_attendee = Attendee.query.get(r.primary_attendee)

                relationships_with_attendee.append((relationship_attendee, r.relationship_code))

        number_of_attendees -= 1

    return relationships_with_attendee

relationships = find_relationships()

# relationships prints out the following:
#[(<Attendee attendee_id=34 first_name=Daniel last_name=Ball>, u'must'),
# (<Attendee attendee_id=16 first_name=Amy last_name=Stevens>, u'must'), 
#(<Attendee attendee_id=30 first_name=Maurice last_name=Owens>, u'want'), 
#(<Attendee attendee_id=22 first_name=Kelly last_name=Copeland>, u'must_not')]

def table_assignments():
    # calculate how many tables the user created
    number_of_tables = Table.query.count()

    # create a dictionary of tables and max seats
    tables_dict = {}

    tables = Table.query.all()

    for table in tables:
        tables_dict[table.table_id] = table.max_seats

    # iterate through the dictionary and assign attendees
    for table_id in tables_dict

        if tables_dict[table.table_id] > 0:
            attendee = Attendee.query.filter_by(attendee_id=attendee).first()
            attendee.table_id = table_id
            db.session.commit()

    # add the relationships for that attendee to the same table


    # delete max number of seats everytime an attendee is assigned to the table









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