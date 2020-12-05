import csv

# import util from parent directory
import os, sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from util import unix_time_millis

def track_growth(school, school_file, join_date_file):
	# create sorted list of join dates
	join_dates = []

	with open(join_date_file, 'r') as file:
		for order in csv.DictReader(file):
			if order['school'] == school:
				join_dates.append(unix_time_millis(order['first_order_date']))

	join_dates.sort()
	# time skip = one week in millis
	cur_time, time_skip = join_dates[0], 604800000
	# track cummulative joinings up until cur_time
	time_count = {}

	for i in range(len(join_dates)):
		date = join_dates[ind]
		while date > cur_time:
			time_count[cur_time] = i - 1
			cur_time += time_skip

	print(time_count)

track_growth(school='brown', school_file=os.getcwd() + '/data/bigfiles/student_join_date.txt', join_date_file=os.getcwd() + ?)


