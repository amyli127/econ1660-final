import glob
import os
import json
import csv

# assigns net order counts for each user
def parse_order_count(file_name=os.getcwd() + '/data/bigfiles/master_orders.txt'):
	counts = {}

	with open(file_name, "r") as file:
		print('parsing: ' + file_name)

		dict_reader = csv.DictReader(file)

		for row in dict_reader:
			fromUser, toUser = row['fromUser'], row['toUser']

			if fromUser not in counts:
				counts[fromUser] = [0, 0]
			if toUser not in counts:
				counts[toUser] = [0, 0]

			counts[fromUser][0] += 1
			counts[toUser][1] += 1

	with open(os.getcwd() + '/data/bigfiles/order_count.txt', 'w', newline='') as order_counts:
		order_count_writer = csv.DictWriter(order_counts, fieldnames=['_id', 'sent', 'received'])
		order_count_writer.writeheader()

		for key in counts:
			order_count_writer.writerow({'_id': key, 'sent': counts[key][0], 'received': counts[key][1]})

parse_order_count()

print('done!')