__author__ = 'Grindlemire'


import json


def write_to_file(jsonData):
    with open('json_db.json', 'w') as outfile:
         json.dump(jsonData, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


def read_all_from_file():
    with open('json_db.json', 'r') as outfile:
        students = json.load(outfile)
        return students



def get_student_from_file(json_file):
    pass


if __name__ == "__main__":
    write_to_file({'5':4, '6':3})
