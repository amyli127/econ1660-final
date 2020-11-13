import glob
import os
import json
import csv

print('NOTE: all txt files in bigfiles/raw/orders must be raw orders data')

print('starting jobs')

# generate congregated, clean data file from raw

objs = []

# parses file into object form

def parse(i, file_name):
	temp_file = 'temp' + str(i) +'.txt'

	with open(temp_file, "w") as clean_file:
		with open(file_name, "r") as file:

			print('parsing: ' + file_name)

			for i, line in enumerate(file):

				if i == 0:
					clean_file.write('{')
					continue

				line = list(line)

				if len(line) < 3:
					clean_file.write("".join(line))
					continue

				if line[-2] == ' ' and line[-3] == '.':
					line[-3] = ','
					line[-2] = '\n'

				line = "".join([el if el != '=' else ':' for el in line])
				clean_file.write(line)

	with open(temp_file, "r") as clean_file:
		temp = json.loads(clean_file.read())
		objs.append(temp)
	
	os.remove(temp_file)

order_files = glob.glob(os.getcwd() + '/bigfiles/raw/orders/*.txt')
for i, file_name in enumerate(order_files):
	parse(i, file_name)


print('finished parsing')
print('writing clean to orders, users, stores...')

# write to congregated csv, cleanly

with open('bigfiles/master_orders.txt', 'w', newline='') as orders, open('bigfiles/master_users.txt', 'w', newline='') as users, open ('bigfiles/master_stores.txt', 'w', newline='') as stores:
	order_writer = csv.DictWriter(orders, fieldnames=['_id', 'message', 'fromUser', 'toUser', 'purchaseId', 'status', 'store', 'createdAt', 'updatedAt', '__v'])
	user_writer = csv.DictWriter(users, fieldnames=['_id', 'firstName', 'username', 'number'])
	store_writer = csv.DictWriter(stores, fieldnames=['_id', 'name'])
	order_writer.writeheader()
	user_writer.writeheader()
	store_writer.writeheader()

	# potential repeat elements
	users_map, stores_map = {}, {}
	bad_order_count, bad_user_count, bad_store_count = 0, 0, 0

	for obj in objs:
		for el in obj['gifts']:

			# write order

			nested_keys = ['fromUser', 'toUser', 'store']
			removable_keys = ['numPoints', 'storeCredit', 'globalCredit', 'rewardTemplate', 'isBirthdayGift', 'rewardId', 'public', 'isFromBirthdayPromo']
			
			subset = {key: val for key, val in el.items() if (key != nested_keys[0] and key != nested_keys[1] and key != nested_keys[2])}

			try:
				subset['fromUser'] = el[nested_keys[0]]['_id']
				subset['toUser'] = el[nested_keys[1]]['_id']
				subset['store'] = el[nested_keys[2]]['_id']

				for key in removable_keys:
					if key in subset:
						del subset[key]
				
				order_writer.writerow(subset)
			except:
				bad_order_count += 1

			# process user

			def process_user(user):
				_id = user['_id']
				if _id not in users_map:
					users_map[_id] = {'_id': 'null', 'firstName': 'null', 'username': 'null', 'number': 'null'}

				for key, val in users_map[_id].items():
					if val == 'null' and key in user:
						users_map[_id][key] = user[key]

			try:
				process_user(el['fromUser'])
			except:
				bad_user_count += 1
			try:
				process_user(el['toUser'])
			except:
				bad_user_count += 1
	
			# process store

			try:
				store = {'_id': el['store']['_id'], 'name': el['store']['name']}

				if store['_id'] not in stores_map:
					stores_map[store['_id']] = store
			except:
				bad_store_count += 1

	print('bad order count: ' + str(bad_order_count))
	print('bad user count: ' + str(bad_user_count))
	print('bad store count: ' + str(bad_store_count))


	# write users + stores

	for _, val in users_map.items():
		user_writer.writerow(val)
	for _, val in stores_map.items():
		store_writer.writerow(val)

print('done!')