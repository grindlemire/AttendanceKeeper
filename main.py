#!/usr/bin/python

"""
Attendance Keeper

A graphical attendance keeper where you can add, motify, delete,
and review each student's attendance record. It also supports
exporting to Excel

author: Joel Holsteen
last modified: July 2014
"""
from Tkconstants import END, LEFT, TOP, X, EXTENDED, MULTIPLE, BOTTOM, BROWSE, W, CENTER, FLAT, GROOVE, E, Y, SUNKEN
import Tkinter as tk
from Tkinter import Tk, RIGHT, BOTH, RAISED, Listbox
from string import atoi
import tkMessageBox
from ttk import Frame, Button, Style, Notebook, Label
from db_controller import *
import Calendar
from edit_dialog import MyDialog


class Main_GUI(Frame):
    student_index = {}
    present_date_index = {}
    absent_date_index = {}
    curStudent = None


    def __init__(self, parent, students):
        Frame.__init__(self, parent)

        self.parent = parent
        self.parent.wm_title("Attendance Keeper")
        self.present_variable = tk.StringVar()
        self.absent_variable = tk.StringVar()
        self.initUI(students)
        self.dates = []
        init_dates(self.dates)

    def initUI(self, students):

        note=Notebook(self.parent)



        #Tabs
        external_tab = Frame(note)
        records_tab = Frame(note)
        edit_tab = Frame(note)
        note.config()
        note.add(external_tab, text = "Attendance")
        note.add(records_tab, text="  Records  ")
        note.add(edit_tab, text="    Edit    ")


        #Create the scrollable list on the left side
        scrollbar = tk.Scrollbar(external_tab, orient="vertical")
        lb = tk.Listbox(external_tab, selectmode=MULTIPLE, width=30, height=20, yscrollcommand=scrollbar.set)
        scrollbar.config(command=lb.yview)
        scrollbar.pack(side="left", fill="y")
        lb.pack(side="left",fill="y")
        self.setList(students, lb)



        #Add dialogue box for new student
        frame1 = Frame(external_tab, relief=GROOVE, borderwidth=0)
        info_frame2 = Frame(records_tab, relief=GROOVE, borderwidth=3)
        name = tk.Entry(frame1)
        name.pack(anchor=CENTER, side=BOTTOM)
        frame1.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)

        #Add the buttons on the right to manipulate the list
        frame = Frame(external_tab, relief=RAISED, borderwidth=0)
        addButton = Button(frame, text="Add Student", command= lambda : self.addStudent(name.get(), lb, lb2, lb3))
        addButton.pack()
        deleteButton = Button(frame, text="Remove Student", command= lambda : self.deleteStudent(lb.curselection(), lb, lb2, lb3))
        deleteButton.pack(anchor=E, pady=20, side=RIGHT)
        frame.pack()

        markCalendarFrame = Frame(external_tab)
        self.markCalendar = Calendar.newCalendar(markCalendarFrame, True)
        markCalendarFrame.pack()

        #Add the reset button and the mark absent button
        frame2 = Frame(external_tab, relief=RAISED, borderwidth=0)
        absentButton = Button(frame2, text="Mark as Absent", command= lambda: self.markAbsent(lb.curselection()))
        absentButton.pack(side=TOP, pady=20)
        resetButton = Button(frame2, text="Reset Today's Attendance", command=self.resetDay)
        resetButton.pack(side=TOP, pady=20)
        frame2.pack(fill=BOTH, expand=1)
        self.pack(fill=BOTH, expand=1)

        #Create the Records Listbox
        scrollbar2 = tk.Scrollbar(records_tab, orient="vertical")
        lb2 = tk.Listbox(records_tab, selectmode=BROWSE, width=30, height=20, yscrollcommand=scrollbar2.set)
        scrollbar2.config(command=lb2.yview)
        scrollbar2.pack(side="left", fill="y")

        #Bind a click to finding attendance
        lb2.bind('<<ListboxSelect>>', self.getTotals)
        lb2.pack(side="left",fill="y")
        self.setList(students, lb2)

        #Create the text that updates in real time based on selection

        self.present_variable.set('')
        self.absent_variable.set('')
        info_frame = Frame(records_tab, relief=GROOVE, borderwidth=3)
        present_setup = tk.Message(records_tab, anchor=W, justify=CENTER, width=100, text="Days Present: ")
        present_setup.pack(fill=X, side=TOP)
        present_message = tk.Message(records_tab, anchor=E, justify=CENTER, width=100, textvariable= self.present_variable)
        present_message.pack(fill=X, side=TOP)
        info_frame.pack(side=TOP)




        absent_setup = tk.Message(records_tab, anchor=W, justify=CENTER, width=100, text="Days Absent: ")
        absent_setup.pack(fill=X, side=TOP)
        absent_variable = tk.Message(records_tab, anchor=E, justify=CENTER, width=100, textvariable= self.absent_variable)
        absent_variable.pack(fill=X, side=TOP)
        info_frame2.pack(side=TOP)



        #Create a see Calendar Button
        # calendarButton = Button(records_tab, text="See Specific Days", command= lambda : self.setStudentCalendar(lb2.curselection()))
        # calendarButton.pack(side=TOP)


        calendar_frame = Frame(records_tab, relief=GROOVE, borderwidth=3, width = 300)
        self.theCalendar = Calendar.newCalendar(calendar_frame, False)
        calendar_frame.pack(side=TOP, pady = 20)

        clearCalendarButton = Button(records_tab, text="Clear Calendar", command=self.clearStudentCalendar)
        clearCalendarButton.pack(side=TOP)

        # close and excel buttons
        bottomFrame = Frame(width=20)
        excelButton = Button(bottomFrame, text="Generate Excel", command=self.generateExcel)
        excelButton.pack(side=LEFT, padx=5, pady=5)

        closeButton = Button(bottomFrame, text="Close", command=self.closeButton)
        closeButton.pack(side=RIGHT, padx=10, pady=5)
        bottomFrame.pack(side=BOTTOM)


        scrollbar3 = tk.Scrollbar(edit_tab, orient="vertical")
        lb3 = tk.Listbox(edit_tab, selectmode=BROWSE, width=30, height=20, yscrollcommand=scrollbar3.set)
        scrollbar3.config(command=lb3.yview)
        scrollbar3.pack(side="left", fill="y")
        lb3.bind('<<ListboxSelect>>', self.get_dates)
        lb3.pack(side="left",fill="y")
        self.setList(students, lb3)

        addFrame = Frame(edit_tab)
        remove_date = Button(addFrame, text="Remove Date", command= lambda : self.remove_date(self.lbedit.curselection(), self.lbedit2.curselection(), True))
        remove_date.pack(side=TOP, pady=2)
        add_dates = Button(addFrame, text="Add Date", command= lambda : self.add_date(lb3.curselection()))
        add_dates.pack(side=LEFT, pady=2)
        edit_selection = Button(addFrame, text="Edit Date", command= lambda : self.edit_date(self.lbedit.curselection(), self.lbedit2.curselection()))
        edit_selection.pack(side=LEFT, pady=2)

        addFrame.pack(side=TOP)

        dateFrame = Frame(edit_tab)
        presentLabel = Label(dateFrame, text="Present")
        presentLabel.pack(side=TOP)
        scrollbar4 = tk.Scrollbar(dateFrame, orient="vertical")
        self.lbedit = tk.Listbox(dateFrame, selectmode=BROWSE, width=29, height=9, yscrollcommand=scrollbar4.set)
        self.lbedit.pack(side=TOP)

        absentLabel = Label(dateFrame, text="Absent")
        absentLabel.pack(side=TOP)
        scrollbar5 = tk.Scrollbar(dateFrame, orient="vertical")
        self.lbedit2 = tk.Listbox(dateFrame, selectmode=BROWSE, width=29, height=8, yscrollcommand=scrollbar5.set)
        self.lbedit2.pack(side=TOP, fill="y")

        dateFrame.pack(side=LEFT, fill="y")

        self.pack(fill=BOTH, expand=1)

        note.pack(fill=BOTH, expand=1)





    def addStudent(self, new_student, lb, lb2, lb3):
        addStudent(new_student)
        self.setList(read_all_from_file(), lb)
        self.setList(read_all_from_file(), lb2)
        self.setList(read_all_from_file(), lb3)


    def deleteStudent(self, selected_students, lb, lb2, lb3):
        result = tkMessageBox.askquestion("Deleting Confirmation", "Are you sure you want to permanently remove "+ str(len(selected_students)) + " students?")
        if result == 'yes':
            for every_student in selected_students:
                value = self.student_index[atoi(every_student)]
                delete_student(value)
            self.parent.update_idletasks()
            self.setList(read_all_from_file(), lb)
            self.setList(read_all_from_file(), lb2)
            self.setList(read_all_from_file(), lb3)


    def markAbsent(self, selected_students):
        absentList = []
        for every_student in selected_students:
            value = self.student_index[atoi(every_student)]
            absentList.append(value)
        present = markAttendance(absentList, self.dates, self.markCalendar.nextDay)
        tkMessageBox.showinfo("Attendance confirmation", "Successfully marked "+str(present)+" student(s) present" )


    def resetDay(self):
        clearday(self.markCalendar.nextDay)
        tkMessageBox.showinfo("Attendance Day Reset Confirmation", "Successfully reset today's attendance!" )

    def setList(self, students, lb):
        index=0
        lb.delete(0, END)
        for each_student in sorted(students):
            self.student_index.__setitem__(index, each_student)
            lb.insert(END,each_student)
            index+=1

    def closeButton(self):
        self.parent.destroy()

    def getTotals(self, e):
        student_index = e.widget.curselection()[0]
        student = self.student_index[atoi(student_index)]
        self.present_variable.set(getTotalDays(student, True))
        self.absent_variable.set(getTotalDays(student, False))
        Calendar.delete_active_canvas(self.theCalendar)
        student = self.student_index[atoi(student_index)]
        presentList = getDays(student, True)
        absentList = getDays(student, False)
        Calendar.buildCalendar(self.theCalendar, presentList, absentList)

    def setStudentCalendar(self, selected_students):
        Calendar.delete_active_canvas(self.theCalendar)
        student_index = selected_students[0]
        student = self.student_index[atoi(student_index)]
        presentList = getDays(student, True)
        absentList = getDays(student, False)
        Calendar.buildCalendar(self.theCalendar, presentList, absentList)

    def clearStudentCalendar(self):
        Calendar.delete_active_canvas(self.theCalendar)

    def setEditList(self, dates, isPresent):
        index=0
        if isPresent:
            self.lbedit.delete(0, END)
        else:
            self.lbedit2.delete(0, END)
        for date in sorted(dates):
            if isPresent:
                self.present_date_index.__setitem__(index, date)
                self.lbedit.insert(END, date)
            else:
                self.absent_date_index.__setitem__(index, date)
                self.lbedit2.insert(END, date)
            index+=1
        if len(self.present_date_index) == 0 and isPresent:
            self.lbedit.insert(END, "No Days Attended!")
        if len(self.absent_date_index) == 0 and not isPresent:
            self.lbedit2.insert(END, "No Days Absent!")

    def get_dates(self, e):
        self.lbedit.delete(0, END)
        student_index = e.widget.curselection()[0]
        student = self.student_index[atoi(student_index)]
        presentDates = get_student_present_dates_from_file(student)
        absentDates = get_student_absent_dates_from_file(student)
        self.curStudent = student
        self.absent_date_index = {}
        self.present_date_index = {}
        self.setEditList(presentDates, True)
        self.setEditList(absentDates, False)


    def add_date(self, studentSelection):
        if studentSelection and studentSelection[0] < len(self.student_index):
            student = self.student_index[atoi(studentSelection[0])]
        else:
            student = self.curStudent
        d = MyDialog(self.parent, None, student, True, getDays(self.curStudent,True), getDays(self.curStudent, False), True)
        if d.return_tuple and d.return_tuple[0] and d.return_tuple[1]:
            if d.return_tuple[0] in self.dates or tkMessageBox.askquestion("ERROR", "Error! Are you sure that you want to add a date that the rest of the students don't have? (Be very certain you want to do this!)" ) =='yes':
                add_day_to_student(student,d.return_tuple[0],d.return_tuple[1])
            presentDates = get_student_present_dates_from_file(self.curStudent)
            absentDates = get_student_absent_dates_from_file(self.curStudent)
            self.setEditList(presentDates, True)
            self.setEditList(absentDates, False)



    def remove_date(self, presentSelection, absentSelection, showConf):
        if presentSelection:
            presentRemove = self.present_date_index[atoi(presentSelection[0])]
            if not showConf or tkMessageBox.askquestion("Deleting Confirmation", "Are you sure you want to permanently remove the date " + str(presentRemove) +" from " + str(self.curStudent) + " ?") == 'yes':
                remove_student_present_date(self.curStudent, presentRemove)
        if absentSelection:
            absentRemove = self.absent_date_index[atoi(absentSelection[0])]
            if not showConf or tkMessageBox.askquestion("Deleting Confirmation", "Are you sure you want to permanently remove the date " + absentRemove +" from " + self.curStudent + " ?") == 'yes':
                remove_student_absent_date(self.curStudent, absentRemove)
        presentDates = get_student_present_dates_from_file(self.curStudent)
        absentDates = get_student_absent_dates_from_file(self.curStudent)
        self.setEditList(presentDates, True)
        self.setEditList(absentDates, False)


    def edit_date(self, presentSelection, absentSelection):
        if presentSelection:
            presentEdit = self.present_date_index[atoi(presentSelection[0])]
            d = MyDialog(self.parent, presentEdit, self.curStudent, True, getDays(self.curStudent,True), getDays(self.curStudent, False), False)
            if d.return_tuple[1] == "Absent":
                if d.return_tuple[0]:
                    if d.return_tuple[0] in self.dates or tkMessageBox.askquestion("ERROR", "Error! Are you sure that you want to add a date that the rest of the students don't have? (Be very certain you want to do this!)" ) =='yes':
                        self.remove_date(presentSelection, absentSelection, False)
                        add_day_to_student(self.curStudent,d.return_tuple[0], d.return_tuple[1])
                else:
                    self.remove_date(presentSelection, absentSelection, False)
                    add_day_to_student(self.curStudent,d.date, d.return_tuple[1])
            if d.return_tuple[1] == "Present":
                if d.return_tuple[0]:
                    if d.return_tuple[0] in self.dates or tkMessageBox.askquestion("ERROR", "Error! Are you sure that you want to add a date that the rest of the students don't have? (Be very certain you want to do this!)" ) =='yes':
                        self.remove_date(presentSelection, absentSelection, False)
                        add_day_to_student(self.curStudent,d.return_tuple[0], d.return_tuple[1])
                else:
                    self.remove_date(presentSelection, absentSelection, False)
                    add_day_to_student(self.curStudent,d.date, d.return_tuple[1])
        if absentSelection:
            absentEdit = self.absent_date_index[atoi(absentSelection[0])]
            d = MyDialog(self.parent, absentEdit, self.curStudent, False, getDays(self.curStudent,True), getDays(self.curStudent, False), False)
            if d.return_tuple[1] == "Present":
                if d.return_tuple[0]:
                    if d.return_tuple[0] in self.dates or tkMessageBox.askquestion("ERROR", "Error! Are you sure that you want to add a date that the rest of the students don't have? (Be very certain you want to do this!)" ) =='yes':
                        self.remove_date(presentSelection, absentSelection, False)
                        add_day_to_student(self.curStudent,d.return_tuple[0], d.return_tuple[1])
                else:
                    self.remove_date(presentSelection, absentSelection, False)
                    add_day_to_student(self.curStudent,d.date, d.return_tuple[1])
            if d.return_tuple[1] == "Absent":
                if d.return_tuple[0]:
                    if d.return_tuple[0] in self.dates or tkMessageBox.askquestion("ERROR", "Error! Are you sure that you want to add a date that the rest of the students don't have? (Be very certain you want to do this!)" ) =='yes':
                        self.remove_date(presentSelection, absentSelection, False)
                        add_day_to_student(self.curStudent,d.return_tuple[0], d.return_tuple[1])
                else:
                    self.remove_date(presentSelection, absentSelection, False)
                    add_day_to_student(self.curStudent,d.date, d.return_tuple[1])
        presentDates = get_student_present_dates_from_file(self.curStudent)
        absentDates = get_student_absent_dates_from_file(self.curStudent)
        self.setEditList(presentDates, True)
        self.setEditList(absentDates, False)

    def generateExcel(self):
        write_to_excel(self.dates)
        tkMessageBox.showinfo("Generation Confirmation", "Excel sheet generated! Open the file called 'excel_db.csv' in Excel to view!" )




def main():

    root = Tk()
    root.geometry("550x500+300+300")

    students = read_all_from_file()
    myApp = Main_GUI(root, students)
    root.mainloop()


if __name__ == '__main__':
    main()

