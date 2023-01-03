import requests
from bs4 import BeautifulSoup as bs
import calendar
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from datetime import date, datetime, timedelta
import os
from pathlib import Path
from dateutil.parser import parse
from dateutil import parser
import re

#Define remove_html to remove html tags from string
regex = re.compile(r'<[^>]+>')
def remove_html(string):
    return regex.sub('', string)

# Define url for Palo Santo classes
url = 'https://www.palosantowellnessboutique.com/yogaschedule'

# Define days of the week, today's date, and timezone
days = dict(zip(calendar.day_name, range(7)))
today = date.today()
eastern = pytz.timezone("America/New_York")

# Pull in the html data from url
hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
}
r = requests.get(url, headers=hdr)
soup = bs(r.content, "html.parser")
mydays = soup.find_all('div',{'class': 'sqs-block-content'})

# Initiate calendar
cal = Calendar()

for elem in mydays:
	try:
		eventday = elem.find('h1').text.strip().title()
		try:
			days[eventday]
			print(eventday)

			myclasses = elem.find_all('p')

			# Loop through shows and add details to calendar
			for thisclass in myclasses:

				try:

					# Get teacher
					teacher = thisclass.text[thisclass.text.rfind(':')+1:].strip()
					print(teacher)

					# Get class time
					try:
						time = thisclass.find('strong').contents[2].strip()
					except TypeError:
						time = thisclass.find('strong').contents[3].strip()

					am_str = time.find('am')
					pm_str = time.find('pm')

					if am_str != -1:
						timestr=time[0:am_str]
						start_time = timestr[0:timestr.find('-')]
						start_time = start_time+" am"
						print("Start time is: "+start_time)
						end_time = timestr[timestr.find('-')+1:]
						end_time = end_time+" am"
						print("End time is: "+end_time)
					else:
						timestr=time[0:pm_str]
						start_time = timestr[0:timestr.find('-')]
						start_time = start_time+" pm"
						print("Start time is: "+start_time)
						end_time = timestr[timestr.find('-')+1:]
						end_time = end_time+" pm"
						print("End time is: "+end_time)	

					# Get class title
					title1 = thisclass.find('strong').contents[0].strip()
					title2 = thisclass.find('strong').contents[1].text
					title = title1+' '+title2
					title = title.strip()
					title = title+" with "+teacher
					print(title)

					for i in range(4):

						# Initiate event
						event=Event()

						# Add title to calendar event
						event.add('summary', title)

						# Add times to calendar event
						date = today + timedelta(days=-today.weekday()+days[eventday], weeks=i-1)
						print(date)
						datestr = date.strftime('%m/%d/%y')
						timefull = datestr+" at "+start_time
						endtimefull = datestr+" at "+end_time
						print(timefull)

						newstart = eastern.localize(parse(timefull))
						newend = eastern.localize(parse(endtimefull))

						utcstart = newstart.astimezone(pytz.utc)
						utcend = newend.astimezone(pytz.utc)

						event.add('dtstart', utcstart)
						event.add('dtend', utcend)

						# Add timestamp
						event.add('dtstamp', datetime.now())

						# Add location
						event['location'] = "Palo Santo Yoga & Wellness, 1707 E Passyunk Ave, Philadelphia, PA 19148, USA"

						# Add event description 
						eventdesc = "Registration link: https://clients.mindbodyonline.com/classic/ws?studioid=218661&stype=-7&sView=week&sLoc=0"
						event.add('description', eventdesc)

						# Add event to calendar
						cal.add_component(event)	
	
				except AttributeError:
					continue
				except TypeError:
					continue				
		except KeyError:
			continue
	except AttributeError:
		continue

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'palo_santo_classes.ics'), 'wb')
f.write(cal.to_ical())
f.close()		


