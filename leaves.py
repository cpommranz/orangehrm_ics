#!/usr/bin/env python

import sys
import inspect, os
import MySQLdb
from icalendar import Calendar, Event
from datetime import datetime
from time import time

#connection to database
conn = MySQLdb.connect(host='localhost', user='orangehrm', passwd='******', db='orangehrm_mysql', port=3306)

#create icalendar object for ics-file
cal = Calendar()
cal.add('prodid', '-//orangeHRM2 calendar//yourdomainorwhatever.com//')
cal.add('version', '2.0')

#create a dictionary cursor (column values can be accessed by name instead of position)
cursor = conn.cursor(MySQLdb.cursors.DictCursor)
 
#get employee details like employee number, id, lastname, firstname
cursor.execute("SELECT emp_number, employee_id, emp_lastname, emp_firstname FROM hs_hr_employee")
employee_set = cursor.fetchall()

#get leave types
cursor.execute("SELECT * FROM ohrm_leave_type")
leave_type_set = cursor.fetchall()

#get all leaves
cursor.execute("SELECT * FROM ohrm_leave")
leave_set = cursor.fetchall()

#generate report
#print "Leave Description, Leave Date, Lenght of Leave, Firstname, Lastname"
for leave in leave_set:
    for leave_type in leave_type_set:
        if leave_type["id"] == leave["leave_type_id"]:
            #decode so that german "Umlaute" are printed correct
            leave_description = leave_type["name"].decode("iso-8859-1").encode("utf-8")
            break
 
    for emp_row in employee_set:
        if leave["emp_number"] == emp_row["emp_number"]:
            emp_firstname = emp_row["emp_firstname"].decode("iso-8859-1").encode("utf-8")
            emp_lastname = emp_row["emp_lastname"].decode("iso-8859-1").encode("utf-8")
            break
    #print "%s, %s, %s, %s, %s" % (leave_description, leave["date"], leave["length_days"], emp_firstname,emp_lastname)
    
    #add to icalendar object
    #split leave_date into year, month, day
    year = leave["date"].year
    month = leave["date"].month
    day = leave["date"].day

    #print leave["start_time"]
    arr_start = leave["start_time"].__str__().split(":")
    arr_end = leave["end_time"].__str__().split(":")
    #print (datetime.combine(leave["date"],0)+leave["start_time"]).time()
    #print test.strftime(%y-%m-%d %H:%M:%S)
    #print leave["start_time"].__str__()
    
    #create Calendar event
    print emp_lastname + ", " + emp_firstname
    event = Event()
    event.add('summary', leave_description+" "+emp_firstname+" "+emp_lastname)
    datef_start = '{dt:%Y}{dt:%m}{dt:%d}'.format(dt = leave["date"])
    #print datef_start
    datef_end = datef_start
    event['uid'] = datef_start+str(leave_type["id"])+emp_firstname+emp_lastname
    datef_start = datef_start + " " + leave["start_time"].__str__()
    datef_start = datetime.strptime(datef_start, '%Y%m%d %H:%M:%S')
    print "formated start date: ", datef_start
    #Workaround to get multiday and all-day leaves working with the icalendar lib
    if leave["start_time"] != leave["end_time"]:
        datef_end = datef_end + " " + leave["end_time"].__str__()
        datef_end = datetime.strptime(datef_end, '%Y%m%d %H:%M:%S')
        print "formated end date:   ", datef_end
    else:
        datef_end = datef_start
        print "formated end date:   ", datef_end
    event.add('DTSTART',datef_start , parameters={'VALUE': 'DATE-TIME'})
    event.add('DTEND',datef_end , parameters={'VALUE': 'DATE-TIME'})    
    event.add('dtstamp', datetime(year,month,day,0,10,0,tzinfo=None))
    event.add('priority', 5)
    
    cal.add_component(event)

#write ics-file in script location
path = os.path.dirname(inspect.getfile(inspect.currentframe()))+'/'
icsname = 'leave_calendar.ics'
file = path+icsname
print "file: ", file
f = open(file, 'wb')
f.write(cal.to_ical())
f.close()
