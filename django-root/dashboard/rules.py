import rules


@rules.predicate
def is_course_offering_owner(user, course_offering):
    return user in course_offering.owners.all()

rules.add_perm('dashboard.is_course_owner_offering', is_course_offering_owner)
