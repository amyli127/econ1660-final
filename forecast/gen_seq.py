import argparse
import csv
import pickle
import dateutil.parser
import os
import copy
import time
import pytz

from datetime import datetime, timedelta


### FEATURE IMPLEMENTATIONS ###

# number of traunches
TRAUNCH_COUNT = 3500 # start date to ~nov 2020 -> should be ~3500

# number of tranches per day
TRANCHES_PER_DAY = 3

def naive_to_est(dt):
	# datetime from snackpass has no timezone (implicitly utc)
	naive = datetime.strptime(dt,"%Y-%m-%dT%H:%M:%S.%fZ")
	
	# explicitly add utc 
	datetime_obj_utc = naive.replace(tzinfo=pytz.timezone('UTC'))

	# convert to eastern
	return datetime_obj_utc.astimezone(pytz.timezone('US/Eastern'))

# datetime obj of first tranche, based on first order at 2017-06-04 19:30:02.279000+00:003
# update: datetime is set to start of fall 2017 semester
# note: set to first mealtime of day of first order to make tranche conversion easier
# note: this time converts to 12am of 09-03 est
FIRST_TRANCHE_DATETIME = naive_to_est("2017-09-03T04:00:00.0000Z")

# dict of meal to list containing start (inclusive) and end (exclusive) hour of meal
MEALTIMES = {"breakfast": [7, 11], "lunch": [11, 15], "dinner": [15, 21]}

# HELPER FUNCTIONS

# converts datetime to traunch index 
def time_to_traunch_index(dt):
	datetime_obj = naive_to_est(dt)

	# calc difference in days
	difference = datetime_obj.date() - FIRST_TRANCHE_DATETIME.date()
	days_diff = difference.days

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

def is_contiguous(user, cur_ind, prev_ind):
	prev_ind >= 0 and user[cur_ind]['semester'] == user[prev_ind]['semester']

def gen_id_to_date():
	id_to_date = {}
	with open(os.getcwd() + '/data/bigfiles/student_join_date.txt', "rt", encoding="utf8") as join_data:
		join_reader = csv.DictReader(join_data)
		for entry in join_reader:
			id_to_date[entry['_id']] = entry['first_order_date']
	return id_to_date


# STAGE 1

def init_users():

	# dict of every users to timeline (list of traunch)
	users = {}

	### 
	# traunch is a dict containing following features:
	#
	# orders (int): number of orders placed by user in traunch
	# day_of_week (int): day of week (Mon = 0, Tue, Wed, Thu, Fri, Sat, Sun = 6)
	# date (yyyy-mm-dd):
	# meal (str): mealtime of traunch (breakfast, lunch, dinner)
	# semester(int): numbered 1-7
	# 
	###

	with open(os.getcwd() + '/data/bigfiles/master_users.txt', "rt", encoding="utf8") as users_data:
		users_data_reader = csv.DictReader(users_data)
		with open(os.getcwd() + '/data/bigfiles/master_orders.txt', "rt", encoding="utf8") as orders_data:
			orders_data_reader = csv.DictReader(orders_data)
			with open(os.getcwd() + '/data/smallfiles/pvd_stores.txt', "rt", encoding="utf8") as pvd_stores:
				store_reader = csv.DictReader(pvd_stores)
				pvd_store_list = []
				for store in store_reader:
					pvd_store_list.append(store['_id'])
				pvd_students = []
				for order in orders_data_reader:
					if order['store'] in pvd_store_list:
						pvd_students.append(order['fromUser'])
				pvd_students = list(set(pvd_students))
				start_time = time.time()
				for user in users_data_reader:
					if user['_id'] in pvd_students:
						users[user['_id']] = [{'orders': 0} for _ in range(TRAUNCH_COUNT)] # copy.deepcopy(TEMPLATE)
				print("init --- %s seconds ---" % (time.time() - start_time))

	return users

def add_orders():
	with open(os.getcwd() + '/data/bigfiles/master_orders.txt', "rt", encoding="utf8") as orders_data:
		orders_data_reader = csv.DictReader(orders_data)
		for order in orders_data_reader:
			if order['fromUser'] in users:
				traunch_index = time_to_traunch_index(order['createdAt'])
				# negative numbers either not in meal time or before first traunch date
				if traunch_index >= 0 and traunch_index < len(users[order['fromUser']]):
					users[order['fromUser']][traunch_index]['orders'] += 1

def add_day_of_week():
	for _, user in users.items():
		for i, traunch in enumerate(user):
			date = traunch_index_to_date(i)
			traunch['day_of_week'] = date.weekday() 
			traunch['date'] = date.date()

def add_meal():
	for _, user in users.items():
		for i, traunch in enumerate(user):
			traunch['meal'] = traunch_index_to_mealtime(i)

def add_semester_index():
	starts = ["2017-09-03", "2017-11-27", "2018-01-22", "2018-04-01", 
			 	"2018-09-02", "2018-11-25", "2019-01-22", "2019-04-01", 
				"2019-09-02", "2019-12-01", "2020-01-20",
				"2020-09-02"]
	ends = ["2017-11-21", "2017-12-18", "2018-03-24", "2018-05-16", 
			 	"2018-11-18", "2018-12-20", "2019-03-24", "2019-05-16", 
				"2019-11-25", "2019-12-20", "2020-03-19",
				"2020-11-20"]
	indx = [1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 7]

	start_dates = [dateutil.parser.isoparse(start).date() for start in starts]
	end_dates = [dateutil.parser.isoparse(end).date() for end in ends]

	start_dates_set = set(start_dates)
	end_dates_set = set(end_dates)

	for _, user in users.items():
		for i, traunch in enumerate(user):
			date = traunch_index_to_date(i).date()
			if date in start_dates_set:
				traunch['semester'] = indx[start_dates.index(date)]
			elif date in end_dates_set:
				traunch['semester'] = -1
			else:
				traunch['semester'] = user[i - 1]['semester']

# must be called before pruning inactive user traunches
def add_avg_order_per_person_aggregate():
	id_to_date = gen_id_to_date()
	vals = []
	for i in range(TRAUNCH_COUNT):

		if i == 0 or not is_contiguous(list(users.values())[0], i, i - 1):
			vals.append(None)
			continue

		order_sum, user_count = 0, 0
		for id_, user in users.items():
			# check if user has joined
			user_join_date = id_to_date[id_]
			join_index = time_to_traunch_index(user_join_date)
			if join_index > i - 1:
				continue
			
			user_count += 1
			order_sum += user[i - 1]['orders']

		vals.append(order_sum / max(1, user_count))

	for _, user in users.items():
		for i in range(TRAUNCH_COUNT):
			user[i]['avg_order_per_person_prev_hour'] = vals[i]

### STAGE 1.5

def remove_prior_traunches():
	id_to_date = gen_id_to_date()
	for user_id, user in users.items():
		user_join_date = id_to_date[user_id]
		first_tranche_idx = time_to_traunch_index(user_join_date)
		user = user[first_tranche_idx:]
		users[user_id] = user

### STAGE 2

def past_x(user, t_idx, curr_sem, days):
	order_count = 0
	for i in range(days * TRANCHES_PER_DAY):
		offset = i + 1
		if t_idx - offset >= 0 and user[t_idx - offset]['semester'] == curr_sem:
			order_count += user[t_idx - offset]['orders']
		else:
			return None
	return order_count

def prev_days():
	for mod_user_id, mod_user in user_model.items():
		for t_idx, traunch in enumerate(users[mod_user_id]):
			sem = traunch['semester']
			mod_user[t_idx]['past_24_hrs'] = past_x(users[mod_user_id], t_idx, sem, 1)
			mod_user[t_idx]['past_3_days'] = past_x(users[mod_user_id], t_idx, sem, 3)
			mod_user[t_idx]['past_7_days'] = past_x(users[mod_user_id], t_idx, sem, 7)
			mod_user[t_idx]['past_30_days'] = past_x(users[mod_user_id], t_idx, sem, 30)


### TRAIN + TEST DATA RENDERING ###

# rows = []
# features = ['_id', 'user_id']

###
# rows is a list of data point (dict) containing features:
#
# _id (str): id of entry
# user (str): id of user 
# <features we desire>
#
###


# count = 0
# for user_id, user in users.items():
# 	for traunch in user:
# 		row = {'_id': str(count), 'user_id': user_id}
# 		rows.append(row)
# 		count += 1

# with open(os.getcwd() + '/data/bigfiles/sequence.txt', 'w', newline='') as sequence:
# 	sequence_writer = csv.DictWriter(sequence, fieldnames=features)
# 	sequence_writer.writeheader()
# 	for row in rows:
# 		sequence_writer.writerow(row)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-load1', action='store_true', default=False)
	args = parser.parse_args()

	if args.load1:
		with open('seq_cache1' + '.pickle', 'rb') as f:
			users = pickle.load(f)
	else:
		users = init_users()
		### STAGE 1 EXECUTE
		for label in [init_users, add_meal, add_day_of_week, add_orders, add_semester_index, add_avg_order_per_person_aggregate]:  
			print(label) 
			start_time = time.time()
			label()
			print("--- %s seconds ---" % (time.time() - start_time))

		# save users
		with open('seq_cache1' + '.pickle', 'wb') as f:
		    pickle.dump(users, f)

	### STAGE 1.5 EXECUTE
	start_time = time.time()
	remove_prior_traunches()
	print("rem --- %s seconds ---" % (time.time() - start_time))

	### STAGE 2 EXECUTE
	for label in [prev_days]:
		print(label) 
		start_time = time.time()
		label()
		print("--- %s seconds ---" % (time.time() - start_time))

	# print(user_model['5bbd1921fc545d002dc5299e'][5:200])











