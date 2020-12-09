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
	# percent_orders_this_semester_same_mealtime (num): percent of orders in semester up to current tranche that were at same mealtime
	# percent_orders_this_semester_same_day_of_week (num): percent of orders in semester up to current tranche that were on the same day of week
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

def add_day_info():
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

		if traunch_index_to_mealtime(i) == 'breakfast' or not is_contiguous(list(users.values())[0], i, i - 1):
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

def same_semester(user, idx, offset):
	idx_new = idx - offset
	return idx_new >= 0 and user[idx]['semester'] == user[idx_new]['semester']


def past_x(user, t_idx, days):
	order_count = 0
	for i in range(days * TRANCHES_PER_DAY):
		offset = i + 1
		if same_semester(user, t_idx, offset):
			order_count += user[t_idx - offset]['orders']
		else:
			return None
	return order_count


def prev_days():
	for _, user in users.items():
		for t_idx, traunch in enumerate(user):
			traunch['past_24_hrs'] = past_x(user, t_idx, 1)
			traunch['past_3_days'] = past_x(user, t_idx, 3)
			traunch['past_7_days'] = past_x(user, t_idx, 7)
			traunch['past_30_days'] = past_x(user, t_idx, 30)


# calculates the percentage of orders this semester in the same mealtime
def add_percent_orders_this_semester_same_mealtime():
	for _, user in users.items():
		# initialize dict from semester to dict of mealtime to count
		mealtime_counts = {}
		for i in range(1, 8):
			semester_mealtime_counts = {}	
			for mealtime in MEALTIMES:
				semester_mealtime_counts[mealtime] = 0
			mealtime_counts[i] = semester_mealtime_counts

		for _, traunch in enumerate(user):
			semester = traunch["semester"]
			# skip if not in school semester
			if semester == -1:
				continue

			# calculate percent orders and set field in tranche
			mealtime = traunch["meal"]
			curr_mealtime_orders = mealtime_counts[semester][mealtime]
			tot_orders = mealtime_counts[semester]["breakfast"] + mealtime_counts[semester]["lunch"] + mealtime_counts[semester]["dinner"]
			percent_orders = 0 if tot_orders == 0 else curr_mealtime_orders / tot_orders # TODO: what to return when there haven't been any orders yet?
			traunch["percent_orders_this_semester_same_mealtime"] = percent_orders

			# update mealtime_counts
			mealtime_counts[semester][mealtime] += traunch["orders"]


# calculates the percentage of orders this semester on the same day of week
def add_percent_orders_this_semester_same_day_of_week():
	for _, user in users.items():
		# initialize dict from semester to dict of day of week to count
		day_counts = {}
		for sem in range(1, 8):
			semester_day_counts = {}	
			for day in range(7):
				semester_day_counts[day] = 0
			day_counts[sem] = semester_day_counts

		for _, traunch in enumerate(user):
			semester = traunch["semester"]
			# skip if not in school semester
			if semester == -1:
				continue

			# calculate percent orders and set field in tranche
			day_of_week = traunch["day_of_week"]
			curr_day_orders = day_counts[semester][day_of_week]

			tot_orders = 0		
			for day in range(7):
				tot_orders += day_counts[semester][day]

			percent_orders = 0 if tot_orders == 0 else curr_day_orders / tot_orders
			traunch["percent_orders_this_semester_same_day_of_week"] = percent_orders

			# update day_counts
			day_counts[semester][day_of_week] += traunch["orders"]


def weather_hour_to_est(dt):
	naive = datetime.strptime(dt, "%Y-%m-%d %H:%M:%S +0000 UTC")

	# explicitly add utc 
	#datetime_obj_utc = naive.replace(tzinfo=pytz.timezone('UTC'))

	# convert to eastern
	return naive.astimezone(pytz.timezone('US/Eastern'))


def add_weather():
	with open(os.getcwd() + '/data/bigfiles/weather.csv', 'rt', newline='') as weather_data:
		hour_to_info = {}
		weather_reader = csv.DictReader(weather_data)
		for hour_entry in weather_reader:
			weather_datetime = weather_hour_to_est(hour_entry['dt_iso'])
			hour_to_info[(weather_datetime.date(), weather_datetime.hour)] = {'feels_like': hour_entry['feels_like'], 'rain_past_hour': hour_entry['rain_1h'], 'snow_past_hour': hour_entry['snow_1h']}
		for _, user in users.items():
			for _, traunch in enumerate(user):
				date = traunch['date']
				meal = traunch['meal']
				if meal == 'breakfast':
					weather_info = hour_to_info[(date, 9)]
				elif meal == 'lunch':
					weather_info = hour_to_info[(date, 13)]
				else:
					weather_info = hour_to_info[(date, 18)]
				traunch['feels_like'] = float(weather_info['feels_like'] or 0)
				traunch['rain_past_hour'] = float(weather_info['rain_past_hour'] or 0)
				traunch['snow_past_hour'] = float(weather_info['snow_past_hour'] or 0)
				

### STAGE 3

def filter_features():
	rows = []
	features = ['orders', 'day_of_week', 'meal', 'semester', 'avg_order_per_person_prev_hour', 'past_24_hrs', 'past_3_days', 'past_7_days', 'past_30_days', \
				"percent_orders_this_semester_same_mealtime", "percent_orders_this_semester_same_day_of_week", 'feels_like', 'rain_past_hour', 'snow_past_hour']

	for user_id, user in users.items():
		for traunch in user:
			row = {}
			for el in features:
				row[el] = traunch[el]
			rows.append(row)

	with open(os.getcwd() + '/data/bigfiles/sequence.txt', 'w', newline='') as sequence:
		sequence_writer = csv.DictWriter(sequence, fieldnames=features)
		sequence_writer.writeheader()
		for row in rows:
			sequence_writer.writerow(row)


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('-load1', action='store_true', default=False)
	args = parser.parse_args()

	if args.load1:
		with open(os.getcwd() + '/data/bigfiles/seq_cache1' + '.pickle', 'rb') as f:
			users = pickle.load(f)
	else:
		users = init_users()
		### STAGE 1 EXECUTE
		for label in [add_meal, add_day_info, add_orders, add_semester_index, add_avg_order_per_person_aggregate]:  
			print(label) 
			start_time = time.time()
			label()
			print("--- %s seconds ---" % (time.time() - start_time))

		# save users
		with open(os.getcwd() + '/data/bigfiles/seq_cache1' + '.pickle', 'wb') as f:
		    pickle.dump(users, f)

	### STAGE 1.5 EXECUTE
	start_time = time.time()
	remove_prior_traunches()
	print("rem --- %s seconds ---" % (time.time() - start_time))

	### STAGE 2 EXECUTE
	for label in [prev_days, add_weather, add_percent_orders_this_semester_same_mealtime, add_percent_orders_this_semester_same_day_of_week]:
		print(label) 
		start_time = time.time()
		label()
		print("--- %s seconds ---" % (time.time() - start_time))

	print(users['5bbd1921fc545d002dc5299e'][:4])

	### STAGE 3 EXECUTE

	filter_features()
