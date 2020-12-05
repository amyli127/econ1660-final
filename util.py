import datetime

# convert a time given in the raw form (ex. 2019-03-23T13:07:47.972Z) to milliseconds from some fixed time
def unix_time_millis(dt):
    epoch = datetime.datetime.utcfromtimestamp(0)
    return (dt - epoch).total_seconds() * 1000

# convert a time in milliseconds from fixed time to raw form (ex. 2019-03-23T13:07:47.972Z)
def unix_date_time(millis):
	pass