# Nuclear fuel Cycle Facilities Database
# Still cleaning this one up ...
# Note: this site would be best scraped with Selenium, but this code was attempts to collect without it 
# (for novice end user friendliness and computers with restrictive company managed security policies)

import requests
import pandas as pd
from bs4 import BeautifulSoup as soup
import time
import datetime
import random

start_t = datetime.datetime.now()

DATA_PATH = './DATA/'

url = 'https://infcis.iaea.org/NFCFDB/facility/Details/'
# numbers = list(range(0, 1098)) 
# ISSUE 1: Number doesn't match total results! , current 969 + 1 (for list, due to indexing) at least 1097 , end +1 !!!
# class_=text-danger
# will need to search, incrementing up by one, until this class is hit, then break
# UPDATE ISSUE 1:!!!! Also doesn't work: numbers not sequential. Goes to at least 1097. Based on IAEA number.
# could do continue if list of entries length less than 796, but then not future proof, unless I grab that from https://infcis.iaea.org/NFCFDB/facilities mud-table-page-number-information,
# but the above is failing due to page loading (no Selenium allowed!!!)

s = requests.Session()

# Getting expected entries = Doesn't work
# main = "https://infcis.iaea.org/NFCFDB/facilities"
# response = s.get(main)

# page_soup = soup(response.text, features='html.parser')
# page_info = page_soup.find(class_="mud-table-page-number-information")
# print(page_info)
# end_number = page_info.text.split(' ')[-1]
# print(end_number)

# Getting labels seperately first
response = s.get(url + "1")

page_soup = soup(response.text, features='html.parser')
parent = page_soup.find_all(class_="mud-input-control")

labels = []

for p in parent:
    label = p.find(class_= "mud-input-label")
    labels.append(label.text)

# Now looping to get the data
entries = []
sources = []

progress = 1
n = 0
expected = 796

no_id = []

while len(entries) < expected:
# for n in numbers:
    response = s.get(url + str(n))
    page_soup = soup(response.text, features='html.parser')
    
    # check = page_soup.find(class_="class_=text-danger")

    # if check:
    #     print("No entry")
    #     pass
    # else:
    parent = page_soup.find_all(class_="mud-input-control")

    holding = []
    for p in parent:  
        text = p.find(class_= "mud-input-slot")
        
        holding.append(text.text)

    if len(holding) == 0:
        print("No entry")
        no_id.append(n)
        pass
    else:
        entries.append(holding)
        sources.append(url + str(n))

        print(str(progress) + " of expected " + str(expected) + "(on ID " + str(n) + ")") #str(len(numbers))
        progress +=1
    
    n +=1

    nap = random.uniform(1, 3)
    time.sleep(nap)

# Saving
df = pd.DataFrame(columns=labels, data=entries)
df['Source 1'] = pd.Series(sources)

df.to_csv(DATA_PATH + "infcis" + ".csv", index=False)

df2 = pd.DataFrame(columns=["ID"], data=no_id)
df2.to_csv(DATA_PATH + "infcis_no_entry" + ".csv", index=False)


# Getting runtime
end_t = datetime.datetime.now()
c = end_t - start_t
print("Runtime: " + str(c.seconds))










# url = "https://infcis.iaea.org/NFCFDB/_blazor?id="
# POST = "https://infcis.iaea.org/NFCFDB/_blazor/negotiate?negotiateVersion=1"

# HEADER = {"Referer": "https://infcis.iaea.org/NFCFDB/facility/Details/5"
#           "cookie": """_ga_ZBGD9EBHJG=GS1.1.1703864115.2.1.1703864137.0.0.0; _ga=GA1.1.1141368277.1702830992; cf_clearance=DDSQtdkMWWmw0l8FXPhkN5TUGxJEBAapWbNBihLFESw-1703864115-0-2-83312078.6dd24204.d4307f98-0.2.1703864115; _ga_8SMEF3YN04=GS1.1.1703865061.1.1.1703865259.0.0.0; _ga_6XM9LQ7EP3=GS1.2.1703865171.1.0.1703865171.0.0.0; _ga_J1YZ4051PP=GS1.1.1704136536.7.0.1704136536.0.0.0; SPSESSION=7VxSX4qAOL+Iikmg2PglYXonjP7UsqIwjvs2pGzvq/pYWFWGLMoiVICDstTLJpqclRi/MuQRu4QbWA3BPfkqgJ/sbgBRRIeabzq07mx5vaKcer7CkzHSv80r+6i2N7anJkhLQEdSEo…sRYuxaQDSO9PJrVs+q6ICo9tlnNadhm4479b9Pw15J+QCW6m2h0J6c3iJWaRxYX2rl95uZ6DxmcbcyTnK4uA8DsaezkhIokx3dRwqiFRp/Vw07Ez9xO16YTWgMVWB26eP6UI2fIGjsT+Kwab2uckUgl2B49sH5fQFE+MuWeuvLm1CeRJ8cv/I+kMeXFv3WlaveUduUkK0+mFZ5b60deijhIlH2KIgOppqLSwX4r4z7DhbZYxScnEEy+c05rTXlLFNp1Zqr0K1AVD7z/vMd0YR6yQ3HoxoTPBv3bXUM5VWCqxVDKKN5kPWdrvie2JTM+PgOGBm5BJ/5aiscNqaUCSDan9Tc+/S0u97MbzPWyLrcVC4WeE+RnuRD4OFRSBD5dO6ve1lmBeHSQP9/CTMxK4mhYncLdc/0uXy/91AObtSY9HwFsOttChKA0vqTiPt94Qy5WNXxYFJ; _ga_R6F4R9JEX4=GS1.1.1704233788.1.1.1704238518.0.0.0""""
# }

# 1704238519 247
# 1702830992
# 1703864115
# s = requests.Session()
# # response = s.get(url)
# response = s.post(POST, headers=HEADER) # gets us an ID

# # print(response.text)
# data = response.json()
# print(data)
# print(data["connectionToken"])
# DATA ="+ÀµEndInvokeJSFromDotNetÃ­[2,true,null]"
# DATA2 = """{"protocol":"blazorpack","version":1}"""

# response = s.post(url + data["connectionToken"], headers=HEADER, data=DATA2)

# print(response)
# print(response.text)

# print(vars(response).keys())

# print("------------------------------------")

# end = "&_=1704236847665"

# response2 = s.get(url + data["connectionToken"] + end, headers=HEADER)

# print(response2)
# print(vars(response2).keys())
# print(response2.text)

# df = pd.json_normalize(data["data"])

# # add date
# df.to_csv(DATA_PATH + "research.csv", index=False)
