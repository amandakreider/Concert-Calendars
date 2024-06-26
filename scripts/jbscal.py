import requests
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

# Define url for JBs events
url = 'https://johnnybrendas.com/events/'

# Define timezone
eastern = pytz.timezone("America/New_York")

# Pull in the html data from url
hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:101.0) Gecko/20100101 Firefox/101.0'
}
r = requests.get(url, headers=hdr)
soup = bs(r.content, "html.parser")
myevents = soup.find_all('div', {'class': 'col-12 eventWrapper rhpSingleEvent h-100 p-0'})

# Define parse_future fn
def parse_future(timestr, default, **parse_kwargs):
    """Same as dateutil.parser.parse() but only returns future dates."""
    now = default
    for _ in range(401):  # assume gregorian calendar repeats every 400 year
        try:
            dt = parser.parse(timestr, default=default, **parse_kwargs)
        except ValueError:
            pass
        else:
            if dt > now: # found future date
                break
        default += relativedelta(years=+1)
    else: # future date not found
        raise ValueError('failed to find future date for %r' % (timestr,))
    return dt

# Initiate lists
links = []
titles = []
dates = []
doortimes = []
venues = []

# Initiate calendar
cal = Calendar()

# Uncomment to add attendees
#cal.add('Attendee 1', 'MAILTO:attendee1@gmail.com')

# Loop through shows and add details to calendar
for elem in myevents:

	# Initiate event
	event = Event()

	# Grab link to individual show
	eventurl = elem.find('a').get('href')
	links.append(eventurl)
	eventreq = requests.get(eventurl,headers=hdr)
	eventsoup = bs(eventreq.content, 'html.parser')

	# Grab title
	title = elem.find('a', {'id': 'eventTitle'}).get('title')
	titles.append(title)

	# Grab date
	date = elem.find('div', {'id': 'eventDate'}).text.replace('\n', '').replace('\t', '')
	date = parse_future(date, default=datetime.now() - timedelta(days=1)).date().strftime('%m/%d/%y')

	# Grab venue
	if elem.find('a', {'class': 'venueLink'}):
		venue = elem.find('a', {'class': 'venueLink'}).text	
		venues.append(venue)
	else:
		venue = ''
		venues.append(venue)

	# Grab door time
	doors = elem.find('div', {'class': 'eventDoorStartDate'}).text.replace('\n', '').replace('\t', '').replace('Doors: ','')
	doortimes.append(doors)

	# Grab event description
	eventdesc = eventsoup.find('div', {'class': 'singleEventDescription'}).text

	# Grab showtime
	searchstart = eventdesc.find('Doors')+5
	searchend = searchstart+12
	search=eventdesc[searchstart:searchend]
	print(search)

	index = search.find('–')
	if index != -1:
		showtime = search[:index].strip()
	else:
		showtime = doors

	# Add title to calendar event
	event.add('summary', title)

	# Add showtimes to calendar event
	timefull = date+" at "+showtime
	dates.append(timefull)
	start_time = eastern.localize(parse(timefull))
	end_time = start_time + timedelta(hours=2)	
	print(title)
	print(start_time)
	print(end_time)

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
	event.add('description', eventdesc)

	# Add event to calendar
	cal.add_component(event)	

# Create a csv file with event info
df = pd.DataFrame()

df['Show'] = titles
df['Date'] = dates
df['Doors'] = doortimes
df['Location'] = venues
df['Link'] = links

directory = str(Path(__file__).parent.parent) + "/csv/"
print("csv file will be generated at ", directory)
df.to_csv(directory+'jbs_events.csv')

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'jbs_events.ics'), 'wb')
f.write(cal.to_ical())
f.close()
