import requests
import json
from bs4 import BeautifulSoup as bs
import pandas as pd
from icalendar import Calendar, Event, vCalAddress, vText
import pytz
from pytz import timezone
from datetime import date, datetime, timedelta
import os
from pathlib import Path

# Define start and end date parameters to insert into URL (today + 365 days)
d1 = '{dt.month}/{dt.day}/{dt.year}/'.format(dt = datetime.now())
d2 = date.today() + timedelta(days=365)
d2 = '{dt.month}/{dt.day}/{dt.year}/'.format(dt = d2)

# Define json url for Fillmore events
url = "https://www.thefillmorephilly.com/api/EventCalendar/GetEvents?startDate="+d1+"&endDate="+d2+"&venueIds=17019,17012&limit=200&offset=1&genre=&artist=&priceLevel=&offerType=STANDARD"
eastern = timezone('US/Eastern')

# Pull in json data from url
r = requests.get(url)
soup = bs(r.content, "html.parser")
json_data = soup.text
data = json.loads(json_data)
json_object = json.loads(data)

# Uncomment to create a .csv file with all event data
#df = pd.DataFrame(json_object['result'])
#df.to_csv('concerts_fillmore.csv')

# Initiate calendar
cal = Calendar()

# Uncomment to add attendees
#cal.add('Attendee 1', 'MAILTO:attendee1@gmail.com')

# Loop through shows and add details to calendar
for i in range(len(json_object['result'])):

	start_time = datetime.strptime(json_object['result'][i]['eventTime'], '%Y-%m-%dT%H:%M:%S').astimezone(eastern)
	end_time = start_time + timedelta(hours=2)

	event = Event()

	# Show titles
	if json_object['result'][i]['isPostponed'] == False & json_object['result'][i]['soldOut'] == False:
		title = json_object['result'][i]['title']
	elif json_object['result'][i]['isPostponed'] == True & json_object['result'][i]['soldOut'] == False:
		title = "Postponed: "+json_object['result'][i]['title']
	elif json_object['result'][i]['soldOut'] == True & json_object['result'][i]['isPostponed'] == False:
		title = "SOLD OUT: "+json_object['result'][i]['title']
	elif json_object['result'][i]['soldOut'] == True & json_object['result'][i]['isPostponed'] == True:
		title = "Postponed: "+json_object['result'][i]['title']

	if json_object['result'][i]['isCancelled'] == True:	
		title = "CANCELLED: "+json_object['result'][i]['title']

	event.add('summary', title)

	# Showtimes
	event.add('dtstart', start_time)
	event.add('dtend', end_time)

	# Timestamp - cal creation
	event.add('dtstamp', datetime.now())

	# Location
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

	# Add artists, on-sale date, ticket url, and genre to event description
	artist_str = ""
	for j in range(len(json_object['result'][i]['artists'])):
		new_artist = json_object['result'][i]['artists'][j]['name'].encode('ascii', 'ignore')
		new_artist = new_artist.decode('ascii')
		artist_str = "%s\n%s" % (artist_str, new_artist)
	artistinfo = "%s\n%s" % ("Artists:", artist_str)	

	sale = "On Sale on"
	saledate = json_object['result'][i]['onsaleOnDate']
	saleinfo = "%s %s" % (sale, saledate)

	url = "Tickets:"
	ticketurl = json_object['result'][i]['ticketUrl']
	urlinfo = "%s %s" % (url, ticketurl)

	genretext = "Genre:"
	genre = json_object['result'][i]['genre']
	genreinfo = "%s %s" % (genretext, genre)

	desc = "%s\n\n%s\n\n%s\n\n%s" % (artistinfo, urlinfo, saleinfo, genreinfo)
	event.add('description', desc)
	#"\\n"

	# Add event to calendar
	cal.add_component(event)

# Save .ics file
directory = str(Path(__file__).parent.parent) + "/calendars/"
print("ics file will be generated at ", directory)
f = open(os.path.join(directory, 'fillmore_events.ics'), 'wb')
f.write(cal.to_ical())
f.close()
