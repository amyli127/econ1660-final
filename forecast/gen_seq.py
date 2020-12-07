import csv
import dateutil.parser
import os
from datetime import datetime, timedelta
import copy

# use pip3 to install
import pytz

### FEATURE IMPLEMENTATIONS ###


# dict of every users to timeline (list of traunch)
users = {}

### 
# traunch is a dict containing following features:
#
# orders (int): number of orders placed by user in traunch
# day_of_week (int): day of week (Mon = 0, Tue, Wed, Thu, Fri, Sat, Sun = 6)
# meal (str): mealtime of traunch (breakfast, lunch, dinner)
# semester(int): numbered 1-7
# 
###

# initialize traunch fields in template
TEMPLATE = {'orders': 0}

# number of traunches
TRAUNCH_COUNT = 3500 # start date to ~nov 2020

# number of tranches per day
TRANCHES_PER_DAY = 3

def naive_to_est(dt):
	# datetime from snackpass has no timezone (implicitly utc)
	naive = datetime.strptime(dt,"%Y-%m-%dT%H:%M:%S.%fZ")
	
	# explicitly add utc 
	datetime_obj_utc = naive.replace(tzinfo=pytz.timezone('UTC'))

	# conver to eastern
	return datetime_obj_utc.astimezone(pytz.timezone('US/Eastern'))


# datetime obj of first tranche, based on first order at 2017-06-04 19:30:02.279000+00:003
# update: datetime is set to start of fall 2017 semester
# note: set to first mealtime of day of first order to make tranche conversion easier
FIRST_TRANCHE_DATETIME = naive_to_est("2017-09-03T00:00:00.0000Z")

# dict of meal to list containing start (inclusive) and end (exclusive) hour of meal
MEALTIMES = {"breakfast": [7, 11], "lunch": [11, 15], "dinner": [15, 21]}

# initialize users
with open(os.getcwd() + '/data/bigfiles/master_users.txt', "rt", encoding="utf8") as users_data:
	users_data_reader = csv.DictReader(users_data)
	for user in users_data_reader:
		users[user['_id']] = [copy.deepcopy(TEMPLATE) for _ in range(TRAUNCH_COUNT)]


# converts datetime to traunch index 
def time_to_traunch_index(dt):
	datetime_obj = naive_to_est(dt)

	# calc difference in days
	difference = datetime_obj - FIRST_TRANCHE_DATETIME
	day_length = timedelta(days=1)
	days_diff, _ = divmod(difference, day_length)

	# convert days difference to tranche difference
	tranche_diff = TRANCHES_PER_DAY * days_diff

	# add 1-3 tranches depending on hour of order
	hour_of_day = datetime_obj.hour
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
def traunch_index_to_mealtime(idx):
	if idx % 3 == 0:
		return 'breakfast'
	elif idx % 3 == 1:
		return 'lunch'
	else:
		return 'dinner'

def traunch_index_to_date(idx):
	days_since_first_tranche = idx / 3
	return FIRST_TRANCHE_DATETIME + timedelta(days=days_since_first_tranche)

def add_orders():
	with open(os.getcwd() + '/data/bigfiles/master_orders.txt', "rt", encoding="utf8") as orders_data:
		orders_data_reader = csv.DictReader(orders_data)
		for order in orders_data_reader:
			datetime = order['createdAt']
			traunch_index = time_to_traunch_index(datetime)
			# -1 means not in meal time
			if traunch_index != -1:
				users[order['fromUser']][traunch_index]['orders'] += 1

def add_day_of_week():
	for _, user in users.items():
		for i, traunch in enumerate(user):
			traunch['day_of_week'] = traunch_index_to_date(i).weekday()

def add_meal():
	for _, user in users.items():
		for i, traunch in enumerate(user):
			traunch['meal'] = traunch_index_to_mealtime(i)

def add_semester_index():
	sems = []
	starts = ["2017-09-03", "2017-11-27", "2018-01-22", "2018-04-01", 
			 	"2018-09-02", "2018-11-25", "2019-01-22", "2019-04-01", 
				"2019-09-02", "2019-12-01", "2020-01-20",
				"2020-09-02"]
	ends = ["2017-11-21", "2017-12-18", "2018-03-24", "2018-05-16", 
			 	"2018-11-18", "2018-12-20", "2019-03-24", "2019-05-16", 
				"2019-11-25", "2019-12-20", "2020-03-19",
				"2020-11-20"]
	indx = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7]
	for i in range(len(indx)):
		# create dictionaries which represent on-campus intervals. usually 2 per semester
		sem = {}
		sem['start_date'] = dateutil.parser.isoparse(starts[i]).astimezone(pytz.timezone('US/Eastern'))
		sem['end_date'] = dateutil.parser.isoparse(ends[i]).astimezone(pytz.timezone('US/Eastern'))
		sem['idx'] = indx[i]
		sems.append(sem)

	for _, user in users.items():
		for i, traunch in enumerate(user):
			date = traunch_index_to_date(i)
			# find interval that contains the given date, -1 if no such interval exists
			for sem in sems:
				if date < sem['start_date']:
					# not a time in which students on campus during a semester
					traunch['semester'] = -1
					break
				elif date >= sem['start_date'] and date <= sem['end_date']:
					traunch['semester'] = sem['idx']
					break
			if 'semester' not in traunch:
				traunch['semester'] = -1

#TODO: create more labels according to this pattern
for label in [add_meal, add_day_of_week, add_semester_index, add_orders]:
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
for user_id, user in users.items():
	for traunch in user:
		row = {'_id': str(count), 'user_id': user_id}
		rows.append(row)
		count += 1

with open(os.getcwd() + '/data/bigfiles/sequence.txt', 'w', newline='') as sequence:
	sequence_writer = csv.DictWriter(sequence, fieldnames=features)
	sequence_writer.writeheader()
	for row in rows:
		sequence_writer.writerow(row)