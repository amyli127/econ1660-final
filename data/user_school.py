import csv

def user_school(orders_file, users_file, stores_school_file):
	# dictionary of store to corresponding school
	store_school = {}

	with open(stores_school_file, 'r') as stores:
		for store in csv.DictReader(stores):
			_id, school = store['_id'], store['school']
			store_school[_id] = school

	# dictionary of student to dictionary of school counts (from orders)
	student_school_count = {}

	with open(orders_file, 'r') as orders:
		for order in csv.DictReader(orders):
			fromUser, toUser, store = order['fromUser'], order['toUser'], order['store']
			school = store_school[store]

			if fromUser not in student_school_count:
				student_school_count[fromUser] = {}
			if toUser not in student_school_count:
				student_school_count[toUser] = {}
			if store not in student_school_count[fromUser]:
				student_school_count[fromUser][school] = 0
			if store not in student_school_count[toUser]:
				student_school_count[toUser][school] = 0

			student_school_count[fromUser][school] += 1
			student_school_count[toUser][school] += 1

	# dictionary of student to school
	student_school = {}

	for student in student_school_count:
		school = max(student_school_count[student], key=student_school_count[student].get)
		store_school[student] = school

	print(student_school)