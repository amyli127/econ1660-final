import csv
import dateutil.parser
import os
from datetime import datetime, timedelta


### FEATURE IMPLEMENTATIONS ###


# dict of every users to timeline (list of traunch)
users = {}

### 
# traunch is a dict containing following features:
#
# orders (int): number of orders placed by user in traunch
# day (str): day of week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
# meal (str): mealtime of traunch (breakfast, lunch, dinner)
# semester(int): TODO
# 
###

# initialize traunch fields in template
TEMPLATE = {'orders': 0}

# number of traunches
TRAUNCH_COUNT = -1

# number of tranches per day
TRANCHES_PER_DAY = 3

# datetime obj of first tranche, based on first order at 2017-06-04 19:30:02.279000+00:00
# note: set to first mealtime of day of first order to make tranche conversion easier
FIRST_TRANCHE_DATETIME = dateutil.parser.isoparse("2017-06-04 00:00:01.00000+00:00")

# dict of meal to list containing start (inclusive) and end (exclusive) hour of meal
MEALTIMES = {"breakfast": [7, 11], "lunch": [11, 15], "dinner": [15, 21]}

# initialize users
with open(os.getcwd() + '/../data/bigfiles/master_users.txt', "rt", encoding="utf8") as users_data:
	users_data_reader = csv.DictReader(users_data)
	for user in users_data_reader:
		users[user['_id']] = [TEMPLATE.deepcopy() for _ in range(TRAUNCH_COUNT)]

# converts time to traunch index 
def time_to_traunch_index(time):
	# convert time to datetime
	datetime_obj = dateutil.parser.isoparse(time)

	# calc difference in days
	difference = datetime_obj - FIRST_TRANCHE_DATETIME
	day_length = timedelta(days=1)
	days_diff, _ = divmod(difference, day_length)

	# convert days difference to tranche difference
	tranche_diff = TRANCHES_PER_DAY * days_diff

	# add 1-3 tranches depending on hour of order
	hour_of_day = datetime_obj.hour
	print(hour_of_day)
	if hour_of_day >= MEALTIMES["breakfast"][0] and hour_of_day < MEALTIMES["breakfast"][1]:
		tranche_diff += 1
	elif hour_of_day >= MEALTIMES["lunch"][0] and hour_of_day < MEALTIMES["lunch"][1]:
		tranche_diff += 2
	elif hour_of_day >= MEALTIMES["dinner"][0] and hour_of_day < MEALTIMES["dinner"][1]:
		tranche_diff += 3
	else:
		# TODO: what to return if not during mealtime hours?
		return -1

	# zero indexed
	tranche_index = tranche_diff - 1
	return tranche_index

# converts traunch index to mealtime
def traunch_index_to_mealtime(time):
	#TODO
	pass

# converts time to day
def traunch_index_to_day(time):
	#TODO
	pass

def add_orders():
	with open(os.getcwd() + '/../data/bigfiles/master_orders.txt', "rt", encoding="utf8") as orders_data:
		orders_data_reader = csv.DictReader(orders_data)
		for order in orders_data_reader:
			time = order['createdAt']
			traunch_index = time_to_traunch_index(time)
			users[order['fromUser']][traunch_index]['orders'] += 1

def add_day():
	for _, user in users:
		for i, traunch in enumerate(user):
			traunch['day'] = traunch_index_to_day(i)

def add_meal():
	for _, user in users:
		for i, traunch in enumerate(user):
			traunch['meal'] = traunch_index_to_mealtime(i)

def add_semester_index():
	#TODO
	pass

#TODO: create more labels according to this pattern

for label in [add_orders, add_meal, add_day, add_semester_index, ]:
	label()


### TRAIN + TEST DATA RENDERING ###


rows = []
features = ['_id', 'user_id']

###
# rows is a list of data point (dict) containing features:
#
# _id (str): id of entry
# user (str): id of user 
# <features we desire>
#
###

count = 0
for user_id, user in users:
	for traunch in user:
		row = {'_id': str(count), 'user_id': user_id}
		rows.append(row)
		count += 1

with open(os.getcwd() + '/data/bigfiles/sequence.txt', 'w', newline='') as sequence:
	sequence_writer = csv.DictWriter(sequence, fieldnames=features)
	sequence_writer.writeheader()
	for row in rows:
		sequence_writer.writerow(row)


