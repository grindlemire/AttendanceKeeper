"""
Simple calendar using ttk Treeview together with calendar and datetime
classes.
"""
from Tkconstants import HIDDEN, DISABLED
import calendar
from datetime import time
from twisted.conch.insults.helper import GREEN, BLACK
import time

try:
    import Tkinter
    import tkFont
except ImportError: # py3k
    import tkinter as Tkinter
    import tkinter.font as tkFont

import ttk

def get_calendar(locale, fwday):
    # instantiate proper calendar class
    if locale is None:
        return calendar.TextCalendar(fwday)
    else:
        return calendar.LocaleTextCalendar(fwday, locale)

class Calendar(ttk.Frame):
    # XXX ToDo: cget and configure

    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta


    def __init__(self, daysPresent, daysAbsent, canPress, top, master=None, **kw):

        self.active_canvas = []
        self.currDay = None
        self.nextDay = None
        self.daysPresent = daysPresent
        self.daysAbsent = daysAbsent
        self.top = top
        self.canPress = canPress

        fwday = kw.pop('firstweekday', calendar.MONDAY)
        year = kw.pop('year', self.datetime.now().year)
        month = kw.pop('month', self.datetime.now().month)
        locale = kw.pop('locale', None)
        sel_bg = kw.pop('selectbackground', '#ecffc4')
        sel_fg = kw.pop('selectforeground', '#05640e')

        self._date = self.datetime(year, month, 1)
        self._selection = None # no date selected

        ttk.Frame.__init__(self, top, **kw)

        self._cal = get_calendar(locale, fwday)

        self.__setup_styles()       # creates custom styles
        self.__place_widgets()      # pack/grid used widgets
        self.__config_calendar()    # adjust calendar columns and setup tags
        # configure a canvas, and proper bindings, for selecting dates
        self.__setup_selection(sel_bg, sel_fg)

        # store items ids, used for insertion later
        self._items = [self._calendar.insert('', 'end', values=x)
                            for x in range(6)]
        # insert dates in the currently empty calendar
        self._build_calendar()

        # set the minimal size for the widget
        # self._calendar.bind('<Map>', self.__minsize)

    def __setitem__(self, item, value):
        if item in ('year', 'month'):
            raise AttributeError("attribute '%s' is not writeable" % item)
        elif item == 'selectbackground':
            self._canvas['background'] = value
        elif item == 'selectforeground':
            self._canvas.itemconfigure(self._canvas.text, item=value)
        else:
            ttk.Frame.__setitem__(self, item, value)

    def __getitem__(self, item):
        if item in ('year', 'month'):
            return getattr(self._date, item)
        elif item == 'selectbackground':
            return self._canvas['background']
        elif item == 'selectforeground':
            return self._canvas.itemcget(self._canvas.text, 'fill')
        else:
            r = ttk.tclobjs_to_py({item: ttk.Frame.__getitem__(self, item)})
            return r[item]

    def __setup_styles(self):
        # custom ttk styles
        style = ttk.Style(self.master)
        arrow_layout = lambda dir: (
            [('Button.focus', {'children': [('Button.%sarrow' % dir, None)]})]
        )
        style.layout('L.TButton', arrow_layout('left'))
        style.layout('R.TButton', arrow_layout('right'))

    def __place_widgets(self):
        # header frame and its widgets
        hframe = ttk.Frame(self)
        lbtn = ttk.Button(hframe, style='L.TButton', command=self._prev_month)
        rbtn = ttk.Button(hframe, style='R.TButton', command=self._next_month)
        self._header = ttk.Label(hframe, width=15, anchor='center')
        # the calendar
        self._calendar = ttk.Treeview(self.top, show='', selectmode='none', height=7)

        # pack the widgets
        hframe.pack(in_=self, side='top', pady=4, anchor='center')
        lbtn.grid(in_=hframe)
        self._header.grid(in_=hframe, column=1, row=0, padx=12)
        rbtn.grid(in_=hframe, column=2, row=0)
        self._calendar.pack(in_=self, expand=1, fill='both', side='bottom')

    def __config_calendar(self):
        cols = self._cal.formatweekheader(3).split()
        self._calendar['columns'] = cols
        self._calendar.tag_configure('header', background='grey90')
        self._calendar.insert('', 'end', values=cols, tag='header')
        # adjust its columns width
        font = tkFont.Font()
        maxwidth = max(font.measure(col) for col in cols)
        for col in cols:
            self._calendar.column(col, width=maxwidth, minwidth=maxwidth,
                anchor='e')

    def __setup_selection(self, sel_bg, sel_fg):
        self._font = tkFont.Font()
        self._canvas = canvas = Tkinter.Canvas(self._calendar,
            background=sel_bg, borderwidth=0, highlightthickness=0)
        canvas.text = canvas.create_text(0, 0, fill=sel_fg, anchor='w')


        if self.canPress:
            canvas.bind('<ButtonPress-1>', lambda evt: canvas.place_forget())
            self._calendar.bind('<Configure>', lambda evt: canvas.place_forget())
            self._calendar.bind('<ButtonPress-1>', self._pressed)

    # def __minsize(self, evt):
    #     width, height = self._calendar.master.geometry().split('x')
    #     height = height[:height.index('+')]
    #     self._calendar.master.minsize(width, height)

    def _build_calendar(self):
        year, month = self._date.year, self._date.month

        # update header text (Month, YEAR)
        header = self._cal.formatmonthname(year, month, 0)
        self._header['text'] = header.title()

        self.first_week = self._calendar.set("I002")
        self.second_week = self._calendar.set("I003")
        self.third_week = self._calendar.set("I004")
        self.fourth_week = self._calendar.set("I005")


        self.weeks = [self.first_week, self.second_week, self.third_week, self.fourth_week]
        isPresent = []
        isPresentItem = []
        isAbsent = []
        isAbsentItem = []
        # update calendar shown dates
        cal = self._cal.monthdayscalendar(year, month)

        for indx, item in enumerate(self._items):
            week = cal[indx] if indx < len(cal) else []
            fmt_week = [('%02d' % day) if day else '' for day in week]
            self.format_dict(fmt_week)
            for day in fmt_week:
                date = str(0) + str(month) + "/" + str(day) + "/" + str(year-2000)
                # if date == time.strftime("%x", time.gmtime()):
                #     self.curDay = day
                #     self.curItem = item
                #     self.curColumn = self.get_column(item, day, fmt_week)
                #     self.curDayBbox = self._calendar.bbox(item, self.curColumn)
                if date in self.daysPresent:
                    column = self.get_column(item, day, fmt_week)
                    presentBbox = self._calendar.bbox(item, column)
                    self.highlight(day, presentBbox, color='green')
                    self._calendar.item(item, values=day, tags='present')
                    isPresent.append(date)
                    isPresentItem.append(day)
                if date in self.daysAbsent:
                    column = self.get_column(item, day, fmt_week)
                    presentBbox = self._calendar.bbox(item, column)
                    self.highlight(day, presentBbox, color='red')
                    self._calendar.item(item, values=day, tags='absent')
                    isAbsent.append(date)
                    isAbsentItem.append(day)
                if date == self.currDay:
                    column = self.get_column(item, day, fmt_week)
                    presentBbox = self._calendar.bbox(item, column)
                    self.highlight(day, presentBbox, color='blue')

            self._calendar.item(item, values=fmt_week)







    def get_column(self, item, day, week):
        for each in week:
            if each == day:
                col = self.formated_dict[each]
                return col


    def format_dict(self, fmt_week):
        self.formated_dict= {}
        ctr=0
        for each_date in fmt_week:
            self.formated_dict[each_date] = ctr
            ctr+=1

    def _show_selection(self, text, bbox):
        """Configure canvas for a new selection."""
        x, y, width, height = bbox

        textw = self._font.measure(text)

        canvas = self._canvas

        canvas.configure(width=width, height=height)
        canvas.coords(1, width - textw, height / 2 - 1)
        canvas.itemconfigure(1, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)



    # Callbacks

    def highlight(self, text, bbox, color):
        x, y, width, height = bbox


        textw = self._font.measure(text)

        canvas = Tkinter.Canvas(master=self._calendar)
        # canvas = self._canvas
        canvas.configure(width=width-2, height=height-2, background=color)
        canvas.create_text(12.25,10,text=text)
        # canvas.coords(1, width - textw, height / 2 - 1)
        canvas.itemconfigure(1, text=text)
        canvas.place(in_=self._calendar, x=x, y=y)
        self.active_canvas.append(canvas)



    def _pressed(self, evt):
        # """Clicked somewhere in the calendar."""
        x, y, widget = evt.x, evt.y, evt.widget
        item = widget.identify_row(y)
        column = widget.identify_column(x)

        if not column or not item in self._items:
            # clicked in the weekdays row or just outside the columns
            return

        item_values = widget.item(item)['values']
        if not len(item_values): # row is empty for this month
            return

        text = item_values[int(column[1]) - 1]
        if not text: # date is empty
            return

        bbox = widget.bbox(item, column)
        if not bbox: # calendar not visible yet
            return

        year, month = self._date.year, self._date.month

        # update and then show selection
        text = '%02d' % text

        self.nextDay = str(0) + str(month) + "/" + str(text) + "/" + str(year-2000)


        self._selection = (text, item, column)
        self._show_selection(text, bbox)

    def _prev_month(self):
        """Updated calendar to show the previous month."""
        self._canvas.place_forget()
        daysPres = self.daysPresent
        daysAbs = self.daysAbsent
        delete_active_canvas(self)
        self.daysPresent=daysPres
        self.daysAbsent=daysAbs

        self._date = self._date - self.timedelta(days=1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        buildCalendar(self, daysPres, daysAbs)

    def _next_month(self):
        """Update calendar to show the next month."""
        self._canvas.place_forget()
        daysPres = self.daysPresent
        daysAbs = self.daysAbsent
        delete_active_canvas(self)
        self.daysPresent=daysPres
        self.daysAbsent=daysAbs

        year, month = self._date.year, self._date.month
        self._date = self._date + self.timedelta(
            days=calendar.monthrange(year, month)[1] + 1)
        self._date = self.datetime(self._date.year, self._date.month, 1)
        buildCalendar(self, daysPres, daysAbs)

    # Properties

    @property
    def selection(self):
        """Return a datetime representing the current selected date."""
        if not self._selection:
            return None

        year, month = self._date.year, self._date.month
        return self.datetime(year, month, int(self._selection[0]))


def newCalendar(top, canPress):
    ttkcal = Calendar('', '', canPress, top, firstweekday=calendar.SUNDAY)
    ttkcal.pack(expand=1, fill='both')
    return ttkcal

def buildCalendar(theCalendar, daysPresent, daysAbsent):
    theCalendar.daysPresent = daysPresent
    theCalendar.daysAbsent = daysAbsent
    theCalendar._build_calendar()

def buildEditCalendar(theCalendar, currDay, daysPresent, daysAbsent):
    theCalendar.currDay = currDay
    theCalendar.daysPresent = daysPresent
    theCalendar.daysAbsent = daysAbsent
    theCalendar._build_calendar()

def delete_active_canvas(theCalendar):
    for each in theCalendar.active_canvas:
        each.configure(bg="white", width=0, height=0)
        each.xview_moveto(0.0)
        each.yview_moveto(0.0)
    buildCalendar(theCalendar,'','')