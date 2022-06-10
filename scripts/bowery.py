import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from datetime import date, datetime, timedelta
import os
from pathlib import Path
from dateutil.parser import parse
from dateutil import parser
from dateutil.relativedelta import relativedelta

# Define url(s) for Bowery events
url = 'https://www.bowerypresents.com/info/events/get?scope=all&rows=50&venues=greater-philly'

# Define timezone
eastern = pytz.timezone("America/New_York")

# Pull in the html data from url
hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
}
r = requests.get(url, headers=hdr)
soup = bs(r.content, "html.parser")
time.sleep(10)
myevents = soup.find_all('div', {'class': 'show-item'})

# Initiate lists
links = []
titles = []
dates = []
doortimes = []
venues = []
addresses = []

# Initiate calendar
cal = Calendar()

# Uncomment to add attendees
#cal.add('Attendee 1', 'MAILTO:attendee1@gmail.com')

# Loop through shows and add details to calendar
for elem in myevents:

	# Initiate event
	event = Event()

	# Event data
	eventdata = elem.find('div', {'class': 'show-info-container'})

	# Grab link to individual show
	eventurl = 'https://www.bowerypresents.com'+eventdata.find('a').get('href')
	links.append(eventurl)
	eventreq = requests.get(eventurl,headers=hdr)
	time.sleep(10)
	eventsoup = bs(eventreq.content, 'html.parser')
	eventjson = eventsoup.find('script', {'type': 'application/ld+json'}).text
	data = json.loads(eventjson)

	# Grab title
	title = data['name']

	# Grab supporting acts
	supporting = eventdata.find('div', {'class': 'supporting-acts'}).text.strip()

	# Grab sub-event data
	#eventdata = eventdata.find('ul', {'class': 'info-list'})
	#meta_content = eventdata.find_all('meta')

	# Grab venue
	venue = data['location']['name']
	venues.append(venue)

	# Grab address
	address = data['location']['address']['streetAddress']
	addresses.append(address)

	# Grab date
	timeinfo = eventdata.find('p', {'class': 'list-date'}).text.replace('\n','').replace('\t','').strip()
	date = timeinfo[0:30].strip()

	# Grab door time and showtime
	doorstart = timeinfo.find('Doors')+5
	doors = timeinfo[doorstart:doorstart+15]
	doorend = doors.find(',')
	doors = doors[0:doorend].strip()
	doortimes.append(doors)

	showstart = timeinfo.find('Show:')+5
	showtime = timeinfo[showstart:showstart+15].strip()

	# Add showtimes to calendar event
	timefull = date+' at '+showtime
	dates.append(timefull)

	start_time = eastern.localize(parse(timefull))
	end_time = start_time + timedelta(hours=2)	
	print(title)
	print(start_time)
	print(end_time)

	# Add title to calendar event
	event.add('summary', title)

	# Add times to calendar event
	utcstart = start_time.astimezone(pytz.utc)
	utcend = end_time.astimezone(pytz.utc)

	event.add('dtstart', utcstart)
	event.add('dtend', utcend)

	# Add timestamp
	event.add('dtstamp', datetime.now())

	# Add location
	event['location'] = venue

	# Uncomment to add event organizer details
	#organizer = vCalAddress('MAILTO:sirjonceo@email.com')
	#organizer.params['cn'] = vText('Sir Jon')
	#organizer.params['role'] = vText('CEO')
	#event['organizer'] = organizer

	# Add event description 
	urlinfo = 'Info: '+eventurl
	doorinfo = 'Doors at '+doors
	shows = 'Show starts at '+showtime	

	desc = "%s\n%s\n\n%s\n\n%s\n%s" % (title, supporting, urlinfo, doorinfo, shows)
	event.add('description', desc)		

	# Add event to calendar
	cal.add_component(event)	

# Create a csv file with event info
df = pd.DataFrame()

df['Show'] = titles
df['Date'] = dates
df['Doors'] = doortimes
df['Location'] = venues
df['Address'] = addresses
df['Link'] = links

directory = str(Path(__file__).parent.parent) + "/csv/"
print("csv file will be generated at ", directory)
df.to_csv(directory+'bowery_events.csv')

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'bowery_events.ics'), 'wb')
f.write(cal.to_ical())
f.close()


