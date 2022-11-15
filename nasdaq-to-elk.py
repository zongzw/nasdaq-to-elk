from os import curdir
import os
import sys
import requests
import json

# find it from OneNote: "nasdaq apikey"
if len(sys.argv) != 3:
    print("Usage: %s <apikey> <ticker>" % sys.argv[0])
    sys.exit(1)

apikey = sys.argv[1]
ticker = sys.argv[2]

nasdaqapi = 'https://data.nasdaq.com/api/v3'
elkep = 'http://10.250.11.185:20004'
mainpath = os.path.abspath(sys.argv[0])
curdir = os.path.dirname(mainpath)

payload = ""
headers = {
    'Content-Type': 'application/json'
}

def target_path(ticker):
    return "%s/data_%s" % (curdir, ticker)
def fetch(ticker):
    data_path = target_path(ticker)
    if os.path.exists(data_path):
        return

    url = "%s/datasets/WIKI/%s/data.json?api_key=%s" % (nasdaqapi, ticker, apikey)
    response = requests.request("GET", url, headers=headers, data=payload)
    response.raise_for_status()
    
    jd = response.json()
    with open(data_path, "w") as fw:
      json.dump(jd, fw)

def upload(ticker):
    data_path = target_path(ticker)
    with open(data_path, "r") as fr:
        jd = json.load(fr)
        data = jd['dataset_data']['data']
        for d in data:
            entry = {
                'ticker': ticker,
            }
            for i in range(0, len(jd['dataset_data']['column_names'])):
                entry[jd['dataset_data']['column_names'][i]] = d[i]
            
            entry['@timestamp'] = entry['Date'] + 'T00:00:00.000+0800'
            entry['year'] = int(entry['Date'][0:4])
            entry['month'] = int(entry['Date'][5:7])
            entry['day'] = int(entry['Date'][8:10])
            entry['dayofmonth'] = (entry['month']-1) * 30 + entry['day']
            print(entry)

            response = requests.request("POST", elkep, headers=headers, json=entry)
            response.raise_for_status()

# fetch('FFIV')
# upload('FFIV')
# fetch('DOW')
# upload('DOW')
fetch(ticker)
upload(ticker)