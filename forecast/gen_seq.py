import csv

# dict of every users to timeline (list of traunch)
users = {}

### 
# traunch is a dict containing following features:
#
# order (bool): whether or not order was placed by user in traunch
# day (str): day of week (Mon, Tue, Wed, Thu, Fri, Sat, Sun)
# meal (str): mealtime of traunch (breakfast, lunch, dinner)
# 
###

# initialize traunch fields in template
TEMPLATE = {'order': False}

# number of traunches
TRAUNCH_COUNT = -1

# initialize users
with open(os.getcwd() + '/../data/bigfiles/master_users.txt', "rt", encoding="utf8") as users_data:
	users_data_reader = csv.DictReader(users_data)
	for user in users_data_reader:
		users[user['_id']] = [TEMPLATE.deepcopy() for _ in range(TRAUNCH_COUNT)]

# converts time to traunch index 
def time_to_traunch_index(time)
	#TODO
	pass

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
			date = order['createdAt']
			traunch_index = time_to_traunch_index(time)
			users[order['fromUser']][traunch_index]['order'] = True

def add_day():
	for _, user in users:
		for i, traunch in enumerate(user):
			traunch['day'] = traunch_index_to_day(i)

def add_meal():
	for _, user in users:
		for i, traunch in enumerate(user):
			traunch['meal'] = traunch_index_to_mealtime(i)

#TODO: create more labels according to this pattern

for label in [add_orders, add_meal, add_day]:
	label()

#TODO: PROCESS USERS TO DATA POINTS

#TODO: WRITE DATA

