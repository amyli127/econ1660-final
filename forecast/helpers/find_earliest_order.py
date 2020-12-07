import csv
import dateutil.parser
import os
from datetime import datetime

future_date = "2021-01-01T01:01:01.000Z"
future_date_obj = dateutil.parser.isoparse(future_date)

earliest_date = future_date_obj

with open(os.getcwd() + '/../../data/bigfiles/master_orders.txt', "rt", encoding="utf8") as orders_data:
    orders_data_reader = csv.DictReader(orders_data)
    for order in orders_data_reader:
        time = order['createdAt']
        datetime_obj = dateutil.parser.isoparse(time)
        if datetime_obj < earliest_date:
            earliest_date = datetime_obj

print(earliest_date)
