import time
import json
from csv_writer import writeCSV


def write_to_file(jsonData):
    with open('json_db.json', 'w') as outfile:
         json.dump(jsonData, outfile, sort_keys = True, indent = 4, ensure_ascii=False)


def read_all_from_file():
    with open('json_db.json', 'r') as outfile:
        students = json.load(outfile)
        if students.values() is None:
            students.pop(students, None)
        return students

def get_student_from_file(json_file):
    pass


def delete_student(name):
    source = json.load(open('json_db.json', 'rw'))
    source.pop(name, source[name])
    with open('json_db.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
    source2 = json.load(open('db2excel.json', 'rw'))
    source2.pop(name)
    with open('db2excel.json', 'w') as outfile:
        json.dump(source2, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

def markAttendance(absentList, dates, currDate):
    dates.append(currDate)
    counter = 0
    source = json.load(open('json_db.json', 'r'))
    source2 = json.load(open('db2excel.json', 'r'))
    for students in source:
        if students not in absentList:
            if not currDate in source[students]["Present"]:
                source[students]["Present"].append(currDate)
                source2[students].__setitem__(currDate, "")
            counter+=1
        elif students in absentList:
            if not currDate in source[students]["Absent"]:
                source[students]["Absent"].append(currDate)
                source2[students].__setitem__(currDate, "A")
    with open('json_db.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
    with open('db2excel.json','w') as outfile:
        json.dump(source2, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
    return counter

def clearday(curDate):
    source = json.load(open('json_db.json','r'))
    for students in source:
        if curDate in source[students]["Absent"]:
            source[students]["Absent"].remove(curDate)
        if curDate in source[students]["Present"]:
            source[students]["Present"].remove(curDate)
    with open('json_db.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

def addStudent(new_student):
    source = json.load(open('json_db.json','r'))
    source.__setitem__(new_student,{"Absent" : [], "Present" : []})
    with open('json_db.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)
    source = json.load(open('db2excel.json','r'))
    source.__setitem__(new_student,{})
    with open('db2excel.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)




def getTotalDays(Student, isPresent):
    source = json.load(open('json_db.json','r'))
    if isPresent:
        return len(source[Student]["Present"])
    else:
        return len(source[Student]["Absent"])

def getDays(Student, isPresent):
    source = json.load(open('json_db.json','r'))
    if isPresent:
        return source[Student]["Present"]
    else:
        return source[Student]["Absent"]

def get_student_present_dates_from_file(Student):
    source = json.load(open('json_db.json','r'))
    return source[Student]["Present"]

def get_student_absent_dates_from_file(Student):
    source = json.load(open('json_db.json','r'))
    return source[Student]["Absent"]

def remove_student_present_date(student, day):
    source = json.load(open('json_db.json', 'r'))
    index = source[student]["Present"].index(day)
    source[student]["Present"].pop(index)
    with open('json_db.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

    source = json.load(open('db2excel.json','r'))
    del source[student][day]
    with open('db2excel.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

def remove_student_absent_date(student, day):
    source = json.load(open('json_db.json', 'r'))
    index = source[student]["Absent"].index(day)
    source[student]["Absent"].pop(index)
    with open('json_db.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

    source = json.load(open('db2excel.json','r'))
    del source[student][day]
    with open('db2excel.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

def add_day_to_student(student, day, status):
    source = json.load(open('json_db.json', 'rw'))
    source[student][status].append(day)
    with open('json_db.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

    source = json.load(open('db2excel.json','r'))
    if status == "Absent":
        source[student].__setitem__(day, "A")
    elif status == "Present":
        source[student].__setitem__(day, "")
    with open('db2excel.json','w') as outfile:
        json.dump(source, outfile, sort_keys = True, indent = 4, ensure_ascii=False)

def write_to_excel(dates):
    source = json.load(open('db2excel.json','r'))
    writeCSV(source, dates)

def init_dates(dates):
    source = json.load(open('db2excel.json', 'r'))
    for student, values in source.iteritems():
        for date, value in values.iteritems():
            if date not in dates:
                dates.append(date)


#
#         {
#     "Joel" : [
#         1,
#         2,
#         3,
#         4
#     ],
#     "Krista" : [
#         5,
#         6,
#         7,
#         8
#     ],
#     "Aaron" : [
#         9,
#         10,
#         11,
#         12
#     ]
#
# }
#USE
# {
#     "Aaron": [
#         "07/04/14"
#     ],
#     "April": [
#         "07/03/14",
#         "07/04/14"
#     ],
#     "Joel": [
#         "07/04/14"
#     ],
#     "Krista": [
#         "07/03/14",
#         "07/04/14"
#     ],
#     "Sarah": [
#         "07/03/14",
#         "07/04/14"
#     ]
# }



#  EXCELL
# {
#     "Aaron": {
#         "07/03/14" : "",
#         "07/04/14" : "",
#         "07/05/14" : ""
#
#     },
#     "April": {
#         "07/03/14" : "",
#         "07/04/14" : "X",
#         "07/05/14" : ""
#
#     },
#     "Joel": {
#         "07/03/14" : "",
#         "07/04/14" : "",
#         "07/05/14" : ""
#     },
#     "Krista": {
#         "07/03/14" : "",
#         "07/04/14" : "A",
#         "07/05/14" : ""
#     },
#     "Sarah": {
#         "07/03/14" : "A",
#         "07/04/14" : "A",
#         "07/05/14" : "A"
#     }
# }
