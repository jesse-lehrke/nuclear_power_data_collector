# IAEA Research Reactor Database (RRDB)

import requests
import json
import pandas as pd
import datetime
import time
import random

start_t = datetime.datetime.now()

DATA_PATH = './DATA/'

url = 'https://nucleus.iaea.org/rrdb/api/ReactorListSearch/getreactorlistdetails'

s = requests.Session()
response = s.get(url)

data = response.json()
df = pd.json_normalize(data["data"])

# Gathering all reactor data (861 records last check, bit slow thus look to improve, e.g. multithread like in China repo)
reactors = list(df["rreactorId"])

DATA_PATH = './DATA/'

HEADER = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'}

url = 'https://nucleus.iaea.org/rrdb/api/UserRoleAccess/useraccess'

s = requests.Session()
response = s.get(url)

data = response.json()
token = (data['data']['token'])

HEADER['Authorization'] = "Bearer " + token

reactor_data = []

# reactors = [791, 792] # for testing
sources = []
progress = 0
for reactor in reactors:
    url_2 = "https://nucleus.iaea.org/rrdb/api/reactor/getgeneralinfo/" + str(reactor)

    response = s.get(url_2, headers= HEADER)

    reactor_data.append(response.json()['data'])
    sources.append(url_2)
    
    progress += 1
    print(str(progress) + " of " + str(len(reactors)))

    nap = random.uniform(1, 3)
    time.sleep(nap)

df2 = pd.DataFrame.from_records(reactor_data)
df2['Source 1'] = pd.Series(sources)

#  Adding second source to all rows
df2['Source 2'] = 'https://.iaea.org/rrdb/api/ReactorListSearch/getreactorlistdetails'

# merge df and df2 on "rreactorId"
# merger is renaming _x _y certain columns asit is keeping both, can do on inner merge probably, but then change compare code
df_merged = pd.merge(df, df2, on='rreactorId', how='outer')

#  Adding second source to all rows / NOTE: why did I have this twice, do test run and check
# df2['Source 2'] = 'https://.iaea.org/rrdb/api/ReactorListSearch/getreactorlistdetails'

#Getting facility codes and changing codes to text
response = s.get("https://nucleus.iaea.org/rrdb/api/common/category")

data = response.json()

fac_type_dict = {list(item.values())[0].title(): list(item.values())[1].title() for item in data['data']}

df_merged['rrcatShtDesc'] = df_merged['rrcatShtDesc'].map(fac_type_dict)

# This loose code was here, leaving until I remember why: 
# df_merged = df_merged[fac_type_dict.values()]

#Getting safeguard codes and updating
response = s.get("https://nucleus.iaea.org/rrdb/api/common/safeguard")

data = response.json()
safeguard_dict = {list(item.values())[0]: list(item.values())[1] for item in data['data']}

## TO DO = Make into a function or something with options
df_merged['sguardId'] = df_merged['sguardId'].apply(lambda x: safeguard_dict[x] if x in safeguard_dict.keys() else x) # if you want all IGOs named
# df_merged['sguardId'] = df_merged['sguardId'].map(safeguard_dict) # Same as above, but more concise
#df_merged['sguardId'] = df_merged['sguardId'].apply(lambda x: "Yes" if pd.notnull(x) and "IAEA" in safeguard_dict[x] else "No") # If you just want Yes if IAEA anywhere in text

# SAVING # TO-DO add date from pris.py ? or other dates ??
df_merged.to_csv(DATA_PATH + "rrdb.csv", index=False)

# Getting runtime
end_t = datetime.datetime.now()
c = end_t - start_t
print("Runtime: " + str(c.seconds))



