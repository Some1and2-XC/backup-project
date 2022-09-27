#!/usr/bin/env python3

"""
Python file for running the schedule for installing a new update
"""

from time import sleep
from os import chdir, getcwd, startfile, path
from win10toast_click import ToastNotifier
from run import run

directory = getcwd()

def SendNotification():

	"""
	Function for sending the notification expected
	"""

	global directory, notification

	notification.show_toast(
		title = "Backup",
		msg = "Run Program to Backup SSD Drive",
		icon_path = "icon.ico",
		 # duration = 5,
		callback_on_click = lambda : startfile(path.join(directory, "run.py"))
	)
	chdir(directory) # Does this such that `Search88()` doesn't mess up relative pathing

def FindWaitTime():
	"""
	Gets the amount of time to wait for a certain date
	"""
	from datetime import time, date, timedelta, datetime

	GoodWeekdays = {2, 4} # 2 is Wednesday and 4 is Friday
	SendTime = time(hour = 1, minute = 31, second = 59, microsecond = 0)

	DaySearch = date.today() + timedelta(days = 1) # Gets a date object with todays date informatino
	while DaySearch.weekday() not in GoodWeekdays:
		# Itterates through weekdays until the weekday that it finds is acceptable
		DaySearch += timedelta(days = 1)
	return datetime.combine(DaySearch, SendTime).timestamp() - datetime.now().timestamp()

notification = ToastNotifier()
SendNotification()
while 1:
	SleepTime = FindWaitTime()
	sleep(SleepTime)
	SendNotification()
