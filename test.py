
import calendar
import urllib2
import json
from csv_writer import writeCSV


def main():
    source = json.load(open('db2excel.json','r'))
    writeCSV(source, )


if __name__ == '__main__':
    main()
