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

# Define start and end date parameters to insert into URL (today + 365 days)
d1 = '{dt.month}/{dt.day}/{dt.year}'.format(dt = date.today()-timedelta(days=3))
d2 = '{dt.month}/{dt.day}/{dt.year}'.format(dt = date.today() + timedelta(days=365))

# Define json url for Fillmore events
url = "https://www.thefillmorephilly.com/api/EventCalendar/GetEvents?startDate="+d1+"&endDate="+d2+"&venueIds=17019,17012&limit=200&offset=1&genre=&artist=&priceLevel=&offerType=STANDARD"

# Define timezone
eastern = pytz.timezone("America/New_York")

# Pull in json data from url
r = requests.get(url)
soup = bs(r.content, "html.parser")
json_data = soup.text
data = json.loads(json_data)
json_object = json.loads(data)

# Initiate calendar
cal = Calendar()

# Uncomment to add attendees
#cal.add('Attendee 1', 'MAILTO:attendee1@gmail.com')

# Initiate lists
links = []
titles = []
soldout = []
postponed = []
canceled = []
showtimes = []
showdates = []

# Loop through shows and add details to calendar
for i in range(len(json_object['result'])):

	# Initiate event
	event=Event()

	# Grab start and end time
	start_time = datetime.strptime(json_object['result'][i]['eventTime'], '%Y-%m-%dT%H:%M:%S')
	start_time = eastern.localize(start_time)
	end_time = start_time + timedelta(hours=2)

	showdate = '{dt.month}/{dt.day}/{dt.year}'.format(dt=start_time)
	timestr = start_time.strftime('%I:%M %p')

	showtimes.append(timestr)
	showdates.append(showdate)

	utcstart = start_time.astimezone(pytz.utc)
	utcend = end_time.astimezone(pytz.utc)	

	# Grab title
	if json_object['result'][i]['isCancelled'] == True:
		title = "CANCELED: "+json_object['result'][i]['title']
		postponed.append('N/A')
		canceled.append('Canceled')
		soldout.append('N/A')
		titles.append(title)	
	elif json_object['result'][i]['isPostponed'] == False & json_object['result'][i]['soldOut'] == False:
		title = json_object['result'][i]['title']
		postponed.append('')
		canceled.append('')
		soldout.append('Tickets Available')
		titles.append(title)
	elif json_object['result'][i]['isPostponed'] == True & json_object['result'][i]['soldOut'] == False:
		title = "Postponed: "+json_object['result'][i]['title']
		postponed.append('Postponed')
		canceled.append('')
		soldout.append('Tickets Available')
		titles.append(title)
	elif json_object['result'][i]['soldOut'] == True & json_object['result'][i]['isPostponed'] == False:
		title = "SOLD OUT: "+json_object['result'][i]['title']
		postponed.append('')	
		canceled.append('')
		soldout.append('Sold Out')
		titles.append(title)
	elif json_object['result'][i]['soldOut'] == True & json_object['result'][i]['isPostponed'] == True:
		title = "Postponed: "+json_object['result'][i]['title']
		postponed.append('Postponed')		
		canceled.append('')
		soldout.append('Sold Out')
		titles.append(title)

	# Add title to iCal
	event.add('summary', title)

	# Add showtimes to iCal
	event.add('dtstart', utcstart)
	event.add('dtend', utcend)

	# Add timestamp to iCal
	event.add('dtstamp', datetime.now())

	# Add location to iCal
	ven = json_object['result'][i]['venueName']
	city = json_object['result'][i]['city']
	state = json_object['result'][i]['stateName']
	location = "%s, %s, %s" % (ven, city, state)
	event['location'] = vText(location)

	# Uncomment to add event organizer details
	#organizer = vCalAddress('MAILTO:sirjonceo@email.com')
	#organizer.params['cn'] = vText('Sir Jon')
	#organizer.params['role'] = vText('CEO')
	#event['organizer'] = organizer

	# Add artists, on-sale date, ticket url, and genre
	artist_str = ""
	for j in range(len(json_object['result'][i]['artists'])):
		if j == 0:
			new_artist = json_object['result'][i]['artists'][j]['name'].encode('ascii', 'ignore')
			new_artist = new_artist.decode('ascii')
			artist_str = new_artist
		elif j!= 0:
			new_artist = json_object['result'][i]['artists'][j]['name'].encode('ascii', 'ignore')
			new_artist = new_artist.decode('ascii')
			artist_str = "%s\n%s" % (artist_str, new_artist)
	artistinfo = "%s\n%s" % ("Artists:", artist_str)	

	sdate = parse(json_object['result'][i]['onsaleOnDate'])
	saledate = '{dt.month}/{dt.day}/{dt.year}'.format(dt=sdate)
	saletime = sdate.strftime('%I:%M %p')
	saleinfo = "On sale on %s at %s" % (saledate, saletime)

	url = "Tickets:"
	ticketurl = json_object['result'][i]['ticketUrl']
	urlinfo = "%s %s" % (url, ticketurl)
	links.append(ticketurl)

	genretext = "Genre:"
	genre = json_object['result'][i]['genre']
	genreinfo = "%s %s" % (genretext, genre)

	desc = "%s\n\n%s\n\n%s\n\n%s" % (artistinfo, urlinfo, saleinfo, genreinfo)
	event.add('description', desc)
	#"\\n"

	# Add event to calendar
	cal.add_component(event)

# Create a csv file with event info
df = pd.DataFrame()

df['Show'] = titles
df['Date'] = showdates
df['Showtime'] = showtimes
df['Sold Out?'] = soldout
df['Canceled?'] = canceled
df['Postponed?'] = postponed
df['Link'] = links

directory = str(Path(__file__).parent.parent) + "/csv/"
print("csv file will be generated at ", directory)
df.to_csv(directory+'fillmore_events.csv')

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'fillmore_events.ics'), 'wb')
f.write(cal.to_ical())
f.close()
