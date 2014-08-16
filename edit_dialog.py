from Tkinter import *
import tkSimpleDialog
import Calendar


class MyDialog(tkSimpleDialog.Dialog):

    def __init__(self, parent, date, student, isPresent, daysPresent, daysAbsent, isAdding):
        if isPresent:
            self.status = "Present"
        else:
            self.status = "Absent"
        self.daysPresent = daysPresent
        self.daysAbsent = daysAbsent
        self.isPresent = isPresent
        self.date = date
        self.student = student
        self.return_tuple = []
        self.isAdding = isAdding
        tkSimpleDialog.Dialog.__init__(self, parent)


    def body(self, master):
        v = IntVar()
        if self.isPresent:
            v.set(1)
        else:
            v.set(2)
        if not self.isAdding:
            nameLabel = Label(self, text="Status  " + self.student + " on " + self.date)
            nameLabel.pack()
        else:
            nameLabel = Label(self, text="Please select a date and a status below")
            nameLabel.pack()


        calendar_frame = Frame(self)
        editButton = Button(calendar_frame, pady=10, text="Edit Day", command=self.setStudentCalendar)
        editButton.pack(side=TOP)
        self.theCalendar = Calendar.newCalendar(calendar_frame, True)
        calendar_frame.pack(side=TOP)



        CLASSES = [
            ("Present",1),
            ("Absent",2),
        ]

        def ShowChoice():
            if v.get() == 1:
                self.status = "Present"
            elif v.get() == 2:
                self.status = "Absent"

        for txt, val in CLASSES:
            Radiobutton(master, text=txt, padx = 20, variable=v, command=ShowChoice, value=val).pack(anchor=W)

        return


    def setStudentCalendar(self):
        Calendar.delete_active_canvas(self.theCalendar)
        Calendar.buildEditCalendar(self.theCalendar, self.date, self.daysPresent, self.daysAbsent)


    def apply(self):
        self.return_tuple = [self.theCalendar.nextDay, self.status]