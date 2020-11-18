import csv
from os import path
import datetime


def time_readable():
    basepath = path.dirname(__file__)
    
    writepath = path.abspath(path.join(basepath, "bigfiles/datetime.txt"))
    with open(writepath, 'w') as time_exp:
        writer = csv.writer(time_exp)
        # Note: day_of_week: Monday = 0, Sunday = 6
        writer.writerow(["_id", "createdAt", "date", "month", "day", "year", "time", "hour", "minute", "day_of_week", "secs_since_epch"])
    
        readpath = path.abspath(path.join(basepath, "bigfiles/master_orders.txt"))
        with open(readpath, 'r') as orders:
            csv_reader = csv.DictReader(orders)
            for order in csv_reader:
                _id = order["_id"]
                timestamp = order["createdAt"]
                d = datetime.datetime.strptime(timestamp,"%Y-%m-%dT%H:%M:%S.%fZ")
                writer.writerow([order["_id"], order["createdAt"], d.strftime('%m/%d/%y'), d.month, d.day, d.year, d.strftime('%H:%M'), d.hour, d.minute, d.weekday(), unix_time_millis(d)])

def unix_time_millis(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000

time_readable()