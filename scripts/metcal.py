from bs4 import BeautifulSoup as bs
import pandas as pd
from urllib.request import Request, urlopen
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from pytz import timezone
from datetime import date, datetime, timedelta
import os
from pathlib import Path
from dateutil.parser import parse
import string

#Create soup of events page
url = 'https://themetphilly.com/events/'
hdr = {'User-Agent': 'Mozilla/5.0'}
req = Request(url,headers=hdr)
page = urlopen(req)
soup = bs(page, 'html.parser')

myevents = soup.find_all('div', {'class': 'event-item'})

#Initiate lists
links = []
titles = []
postponed = []
doortimes = []
showtimes = []
dates = []

# Initiate calendar
cal = Calendar()

# Uncomment to add attendees
#cal.add('Attendee 1', 'MAILTO:attendee1@gmail.com')

for elem in myevents:

	cont = elem.find('div', {'class': 'event-link-container'})

	#Grab links
	eventurl=cont.find('a').get('href')
	links.append(cont.find('a').get('href'))

	#Create soup of event link
	eventhdr = {'User-Agent': 'Mozilla/5.0'}
	eventreq = Request(eventurl,headers=hdr)
	eventpage = urlopen(eventreq)
	eventsoup = bs(eventpage, 'html.parser')

	#Check if postponed
	if 'Postponed' in elem.find('a', {'class': 'event-btn btn-accent right-btn'}).text:
		postponed.append('Postponed')
		post = 1
	else:
		postponed.append('')
		post = 0

	#Grab titles
	try:
		if post == 1:
			title = "POSTPONED: "+cont.find('h1').text+": "+cont.find('h2').text
			titles.append("POSTPONED: "+cont.find('h1').text+": "+cont.find('h2').text)
		elif post == 0:
			title = cont.find('h1').text+": "+cont.find('h2').text
			titles.append(cont.find('h1').text+": "+cont.find('h2').text)
	except AttributeError as e:
		title = cont.find('h1').text
		titles.append(cont.find('h1').text)

	printable = set(string.printable)
	title = ''.join(filter(lambda x: x in printable, title))

	#Show date
	date=cont.find('h3').text
	dates.append(date)

	#Grab showtimes
	timedets = eventsoup.find_all('div', {'class': 'event-detail-block'})

	showtime = ''
	doortime = ''

	for det in timedets:
		timetypes=det.find_all('h2')
		for type in timetypes:
			if 'Door' in type.text:
				doortime = type.find('span').string
				doortimes.append(doortime)
			elif 'Event' in type.text:
				showtime = type.find('span').string
				showtimes.append(showtime)

	if showtime == '':
		showtimes.append(showtime)
	if doortime == '':
		doortimes.append(doortime)

	#Grab event descriptions
	eventdesc=eventsoup.find('div', {'class': 'event-description'}).text

	#Initiate event
	event = Event()

	# Show titles
	event.add('summary', title)

	# Showtimes
	timefull = date+" at "+showtime
	start_time = parse(timefull)
	end_time = start_time + timedelta(hours=2)	
	event.add('dtstart', start_time)
	event.add('dtend', end_time)

	# Timestamp - cal creation
	event.add('dtstamp', datetime.now())

	# Location
	location = 'The Met, 858 N Broad St, Philadelphia, PA 19130'
	event['location'] = vText(location)

	# Uncomment to add event organizer details
	#organizer = vCalAddress('MAILTO:sirjonceo@email.com')
	#organizer.params['cn'] = vText('Sir Jon')
	#organizer.params['role'] = vText('CEO')
	#event['organizer'] = organizer

	# Add link, door time, show time, and event description 
	urlinfo = 'Info: '+eventurl
	doors = 'Doors at '+doortime
	shows = 'Show starts at '+showtime

	desc = "%s\n\n%s\n%s\n\n%s" % (urlinfo, doors, shows, eventdesc)
	event.add('description', desc)

	# Add event to calendar
	cal.add_component(event)	

# Create a csv file with event info
df = pd.DataFrame()

df['Show'] = titles
df['Date'] = dates
df['Doors'] = doortimes
df['Showtime'] = showtimes
df['Postponed?'] = postponed
df['Link'] = links

directory = str(Path(__file__).parent.parent) + "/csv/"
print("csv file will be generated at ", directory)
df.to_csv(directory+'met_events.csv')

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'met_events.ics'), 'wb')
f.write(cal.to_ical())
f.close()
