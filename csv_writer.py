import csv
import json
from main import *


def writeCSV(json, dates):

    with open("excel_db.csv", "w") as file:
        csv_file = csv.writer(file)
        rows = [" "]
        for date in sorted(dates):
            rows.append(date)
        csv_file.writerow(rows)
        rows=[]
        rows = []
        for name in sorted(json):
            rows.append(name)
            for date in sorted(json[name]):
                rows.append(json[name][date])
            csv_file.writerow(rows)
            rows=[]