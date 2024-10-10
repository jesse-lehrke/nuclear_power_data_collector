# IAEA Power Reactor Information System
# Personal note as I always forget: python -m ensurepip --default-pip


import requests
from bs4 import BeautifulSoup as soup
import pandas as pd
import time
import datetime
import re
import base64
import random


start_t = datetime.datetime.now()

# specifying cert path did not resolve SSLError: only using 3.9 did, but leaving here for others to find solution (did lots of digging, no luck)
cert_PATH = './INPUTS/iaea-org-chain.pem'
DATA_PATH = './DATA/'

# URLS (core and end seperated for legacy reasons, may have future uses so kept)
core_url = "https://pris.iaea.org/PRIS/CountryStatistics/"
end_url = "CountryDetails.aspx?current="

landing = "https://pris.iaea.org/PRIS/CountryStatistics/CountryStatisticsLandingPage.aspx"

HEADER = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'}

# GET COUNTRY NAMES AND CODES FOR core_url
s = requests.Session()
# s.verify = cert_PATH
# requests.sessions.Session = lambda: s

content = s.get(landing, headers=HEADER) #verify=cert_PATH
page_soup = soup(content.text, features='html.parser')

# finding parent <ul> tag 
parent = page_soup.find(class_="sidebar").find("ul") 
  
# finding all <li> tags 
names = parent.find_all('li')
countries = []
for n in names[1:]: # instead of indexing, better to maybe drop COUNTRIES, for futureproofing
    countries.append(n.text.strip())

codes = []
for n in names[1:]: # instead of indexing, better to maybe drop COUNTRIES, for futureproofing
    codes.append(n.a['href'].split('=')[-1])

# CREATE DATAFRAME, saves one request doing this

df = None

# LOOP THROUGH COUNTRIES

for index, code in enumerate(codes):
    print(countries[index].upper())
    # Fetch data
    s = requests.Session()
    response = s.get(core_url + end_url + code)
    # print(vars(response).keys()) 
    page_soup = soup(response.text, features='html.parser')

    header = page_soup.find('thead')
    names = header.find_all('th')
    column_names = []
    for c in names:
        c = c.text.strip('\t\n\r')
        column_names.append(re.sub(r"\s+", " ", c.strip()))
        # column_names.append(core_url + end_url + code) # Why in God's name did i do this.
    
    # Create df is none exists (just saves one request doing it here)
    if df is None:
        df = pd.DataFrame(columns = ['Country'] + column_names + ['Source_1'])

    # APPROACH 1: Get data
    section = page_soup.find('tbody')

    rows = section.find_all('tr')

    for row in rows:
        column = row.find_all('td')
        n = 0
        for c in column:
            print(column_names[n].upper() + ":  " + c.text.strip())
            n += 1
        
        to_df = [c.text.strip() for c in column]
        to_df = [countries[index]] + to_df + [core_url + end_url + code]
        df.loc[len(df)] = to_df
        print("-------------------------------------")
    
    # Sleeping before next request
    nap = random.uniform(1, 3)
    time.sleep(nap)

# Get last update: useful for continueous monitoring and updating (e.g. see compare.py irrc - might not be updated as of 9.10.2024)
base = page_soup.find('input',{'id':'__VIEWSTATE'})
base = base.get('value')

base64_bytes = base.encode('UTF-8') #convert to bytes
message_bytes = base64.b64decode(base64_bytes) #back to original as bytes
message = message_bytes.decode('UTF-8', "replace")
date = re.search(r'Last update on (.*?)d', message).group(1)
print(date)

#df.to_csv(DATA_PATH + "pris.csv", index=False)
df.to_csv(DATA_PATH + "pris_" + str(date) + ".csv", index=False)

# Getting runtime
end_t = datetime.datetime.now()
c = end_t - start_t
print("Runtime: " + str(c.seconds) + ' seconds')


##############################################################

# INSTALLS for excel integration
# install xlrd (backup) and for xlsx, install openpyxl

## TO DO:
# check if last updated > our current data

# save it all if above true
# random sleep
# continue through list until done

# merge new data with old
