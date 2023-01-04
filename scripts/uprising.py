import calendar
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from datetime import date, datetime, timedelta
import os
from pathlib import Path
from dateutil.parser import parse
from dateutil import parser
import pandas as pd

# Read in csv of Uprising class schedule
csv_dir = str(Path(__file__).parent.parent) + "/csv/"
df = pd.read_csv(csv_dir+'uprising_acm.csv').transpose()
schedule = df.to_dict()

# Define days of the week, today's date, and timezone
days = dict(zip(calendar.day_name, range(7)))
today = date.today()
eastern = pytz.timezone("America/New_York")

# Initiate calendar
cal = Calendar()

# Create weekly calendar events for each yoga class
for h in schedule:

	for i in range(4):

		# Initiate event
		event=Event()

		# Add title to calendar event
		teacher = schedule[h]['teacher'].strip()
		title = schedule[h]['class'].strip()
		title = title + ' with ' + teacher
		event.add('summary', title)
		print(title)

		# Add times to calendar event
		logstart = schedule[h]['time']
		logend = schedule[h]['end_time']

		# Add dates to calendar event
		eventday = schedule[h]['day'].strip()
		date = today + timedelta(days=-today.weekday()+days[eventday], weeks=i-1)
		datestr = date.strftime('%m/%d/%y')
		timefull = datestr+" at "+logstart
		endtimefull = datestr+" at "+logend

		start_time = eastern.localize(parse(timefull))
		end_time = eastern.localize(parse(endtimefull))

		utcstart = start_time.astimezone(pytz.utc)
		utcend = end_time.astimezone(pytz.utc)

		event.add('dtstart', utcstart)
		event.add('dtend', utcend)

		# Add timestamp
		event.add('dtstamp', datetime.now())

		# Add location
		event['location'] = "Uprising ACM, 1839 E Passyunk Ave, Philadelphia, PA 19148"

		# Add event description 
		eventdesc = 'Registration link: https://www.uprisingacm.com/yoga\n\nTeacher: '+teacher+'\n\nTime: '+timefull
		event.add('description', eventdesc)

		# Add event to calendar
		cal.add_component(event)	

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'uprising_classes.ics'), 'wb')
f.write(cal.to_ical())
f.close()		


