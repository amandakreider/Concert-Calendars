# import requests library
import requests

#import beautiful soup
from bs4 import BeautifulSoup as bs

# import pandas
import pandas as pd

# the website URL
# url_link = "http://167.88.153.179/concert-calendar-m"

# result = requests.get(url_link).text
# doc = bs(result, "html.parser")

# my_table = doc.find("tbody")
# tr_tags = my_table.find_all("tr")

# days = []
# for elem in tr_tags:
# 	a_links = elem.find_all(class_ = "cell-1")
# 	for i in a_links:
# 		days.append(i.string)

# dates = []
# for elem in tr_tags:
# 	a_links = elem.find_all(class_ = "cell0")
# 	for i in a_links:
# 		dates.append(i.string)

# artists = []
# res = doc.find_all(class_ = "cell1")
# for elem in res:
# 	artists.append(elem.text)

# venues = []
# for elem in tr_tags:
# 	a_links = elem.find_all(class_ = "cell2")
# 	for i in a_links:
# 		venues.append(i.string)

# age = []
# for elem in tr_tags:
# 	a_links = elem.find_all(class_ = "cell4")
# 	for i in a_links:
# 		age.append(i.string)		

# regions = []
# for elem in tr_tags:
# 	a_links = elem.find_all(class_ = "cell5")
# 	for i in a_links:
# 		regions.append(i.string)		

df = pd.DataFrame()

df['Day'] = days
df['Date'] = dates
df['Artist'] = artists
df['Venue'] = venues
df['Age'] = age
df['Region'] = regions

df.to_csv('concerts.csv')