import csv


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

# initialize users
with open(os.getcwd() + '/../data/bigfiles/master_users.txt', "rt", encoding="utf8") as users_data:
	users_data_reader = csv.DictReader(users_data)
	for user in users_data_reader:
		users[user['_id']] = [TEMPLATE.deepcopy() for _ in range(TRAUNCH_COUNT)]

# converts time to traunch index 
def time_to_traunch_index(time):
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


