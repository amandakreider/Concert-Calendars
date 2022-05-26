from bs4 import BeautifulSoup as bs
from urllib.request import Request, urlopen
import pandas as pd

url = 'https://themetphilly.com/events/'
hdr = {'User-Agent': 'Mozilla/5.0'}
req = Request(url,headers=hdr)
page = urlopen(req)
soup = bs(page)

mydivs = soup.find_all('div', {'class': 'event-link-container'})

#Grab links
links = []
for elem in mydivs:
	a = elem.find('a')
	print(a.get('href'))	
	links.append(a.get('href'))

#Grab links
links = []
for elem in mydivs:
	a = elem.find('a')
	print(a.get('href'))	
	links.append(a.get('href'))








#df['Link'] = links
#df.to_csv('concerts.csv')