import csv
from os import path


def student_join():
    student_to_download_date = {}

    basepath = path.dirname(__file__)
    readpath = path.abspath(path.join(basepath, "bigfiles/master_orders.txt"))
    with open(readpath, 'r') as orders:
        csv_reader = csv.DictReader(orders)
        for order in csv_reader:
            if order["fromUser"] not in student_to_download_date:
                student_to_download_date[order["fromUser"]] = order["createdAt"]
            # TODO @josh: Dates are currently unreadable. I believe this should work. Manual verification looks ok.
            elif order["createdAt"] < student_to_download_date[order["fromUser"]]:
                student_to_download_date[order["fromUser"]] = order["createdAt"]
    
    writepath = path.abspath(path.join(basepath, "bigfiles/student_join_date.txt"))
    with open(writepath, 'w') as stud_join:
        writer = csv.writer(stud_join)
        writer.writerow(["_id", "first_order_date"])
        for ident in student_to_download_date:
            writer.writerow([ident, student_to_download_date[ident]])

student_join()

def store_join():
    store_to_download_date = {}

    basepath = path.dirname(__file__)
    readpath = path.abspath(path.join(basepath, "bigfiles/master_orders.txt"))
    with open(readpath, 'r') as orders:
        csv_reader = csv.DictReader(orders)
        for order in csv_reader:
            if order["store"] not in store_to_download_date:
                store_to_download_date[order["store"]] = order["createdAt"]
            # TODO @josh: Dates are currently unreadable. I believe this should work. Manual verification looks ok.
            elif order["createdAt"] < store_to_download_date[order["store"]]:
                store_to_download_date[order["store"]] = order["createdAt"]
    
    writepath = path.abspath(path.join(basepath, "bigfiles/store_join_date.txt"))
    with open(writepath, 'w') as rest_join:
        writer = csv.writer(rest_join)
        writer.writerow(["_id", "first_order_date"])
        for ident in store_to_download_date:
            writer.writerow([ident, store_to_download_date[ident]])

store_join()