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

# Define url for R5 events
url = 'https://r5productions.com/events/'

# Define timezone
eastern = pytz.timezone("America/New_York")

# Pull in the html data from url
hdr = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:78.0) Gecko/20100101 Firefox/78.0'
}
r = requests.get(url, headers=hdr)
soup = bs(r.content, "html.parser")
myevents = soup.find_all('div', {'class': 'col-12 rhp-event-info'})

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

	# Grab title
	title = elem.find('a', {'class': 'url'}).get('title')

	# Grab tagline (if one exists)
	try:
		tagline = elem.find('div', {'class': 'eventTagLine'}).text.strip()+': '
		title = tagline+title
	except AttributeError as e:
		title = title

	titles.append(title)

	# Grab link to individual show
	eventurl = elem.find('a', {'class': 'url'}).get('href')
	links.append(eventurl)
	eventreq = requests.get(eventurl,headers=hdr)
	eventsoup = bs(eventreq.content, 'html.parser')

	# Grab event page 
	eventinfo = eventsoup.find('div', {'class': 'singleEventDetails p-md-4'})

	# Grab date
	date = eventinfo.find('span', {'class': 'eventStDate'}).text
	date = parse_future(date, default=datetime.now() - timedelta(days=1)).date().strftime('%m/%d/%y')

	# Grab other artists 
	try:
		other_artists = elem.find('h4', {'id': 'evSubHead'}).text.strip()
	except AttributeError as e:
		other_artists = ''

	# Grab door time and showtime
	timeinfo = elem.find('div', {'class': 'eventDoorStartDate'}).text.strip()

	doorstart = timeinfo.find('Doors:')+6
	doorend = doorstart+8
	doors = timeinfo[doorstart:doorend].replace('|','').strip()
	doortimes.append(doors)

	showstart = timeinfo.find('Show:')+6
	showend = showstart+8
	showtime = timeinfo[showstart:showend].replace('|','').strip()

	# Grab venue
	venue = elem.find('a', {'class': 'venueLink'}).text	
	venues.append(venue)

	# Grab event description
	eventdesc = eventinfo.find('div', {'class': 'singleEventDescription'}).text

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
	urlinfo = 'Info: '+eventurl
	doorinfo = 'Doors at '+doors
	shows = 'Show starts at '+showtime	
	artists = 'Other artists: '+other_artists

	desc = "%s\n%s\n%s\n\n%s\n\n%s\n%s\n\n%s" % (title, other_artists, urlinfo, artists, doorinfo, shows, eventdesc)
	event.add('description', desc)		

	#add in title and other artists too!!!

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
df.to_csv(directory+'r5_events.csv')

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'r5_events.ics'), 'wb')
f.write(cal.to_ical())
f.close()
