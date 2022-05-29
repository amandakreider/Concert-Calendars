import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from datetime import date, datetime, timedelta
import os
from pathlib import Path
from dateutil.parser import parse

# Define url for Met events
url = 'https://themetphilly.com/events/'

# Define timezone
eastern = pytz.timezone("America/New_York")

# Pull in the html data from url
hdr = {'User-Agent': 'Mozilla/5.0'}
r = requests.get(url, headers=hdr)
soup = bs(r.content, "html.parser")
myevents = soup.find_all('div', {'class': 'event-item'})

# Initiate lists
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

# Loop through shows and add details to calendar
for elem in myevents:

	# Initiate event
	event = Event()

	# Grab link to individual show
	cont = elem.find('div', {'class': 'event-link-container'})
	eventurl=cont.find('a').get('href')
	links.append(cont.find('a').get('href'))
	eventreq = requests.get(eventurl,headers=hdr)
	eventsoup = bs(eventreq.content, 'html.parser')

	# Check if postponed
	if 'Postponed' in elem.find('a', {'class': 'event-btn btn-accent right-btn'}).text:
		postponed.append('Postponed')
		post = 1
	else:
		postponed.append('')
		post = 0

	# Grab title
	try:
		if post == 1:
			title = "POSTPONED: "+cont.find('h1').text+": "+cont.find('h2').text
			titles.append("POSTPONED: "+cont.find('h1').text+": "+cont.find('h2').text)
		elif post == 0:
			title = cont.find('h1').text+": "+cont.find('h2').text
			titles.append(cont.find('h1').text+": "+cont.find('h2').text)
	except AttributeError as e:
		if post == 1:
			title = "POSTPONED: "+cont.find('h1').text
			titles.append("POSTPONED: "+cont.find('h1').text)
		elif post == 0:
			title = cont.find('h1').text
			titles.append(cont.find('h1').text)

	#printable = set(string.printable)
	#title = ''.join(filter(lambda x: x in printable, title))

	# Grab date
	date=cont.find('h3').text
	dates.append(date)

	# Grab showtime
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

	# Grab event description
	eventdesc=eventsoup.find('div', {'class': 'event-description'}).text	

	# Add title to calendar event
	event.add('summary', title)

	# Add showtimes to calendar event
	timefull = date+" at "+showtime
	start_time = eastern.localize(parse(timefull))
	end_time = start_time + timedelta(hours=2)	
	print(title)
	print(start_time)

	utcstart = start_time.astimezone(pytz.utc)
	utcend = end_time.astimezone(pytz.utc)
	print(utcstart)
	print(utcend)	

	event.add('dtstart', utcstart)
	event.add('dtend', utcend)

	# Add timestamp
	event.add('dtstamp', datetime.now())

	# Add location
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
