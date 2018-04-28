import requests
import json
import time
URL = "https://graph.facebook.com/v2.12/10155083734421479/comments"

params = {
    "access_token" : "EAACEdEose0cBAOA7fjoZBtwopI3W4eXZAOh7w2u4uxVenWAsTm8wvtPSINZAX0r7wZBGu2Soe9gFWa7dOP7qDYb4gTHmAJVVWCtk15DFkwFyiiTHonxWB5Jy8zeRbmHfsa0VbQ5QQtmClQyi2X3oCOZBHqXStmYZBHGU8evwHy0je9BQxhf7cZC6TS9b9mA7yZCX7y9C3jCGZAwZDZD",
    "debug" : "all",
    "format" : "json",
    "method" : "get",
    "pretty" : 0,
    "suppress_http_code" : 1,
    "live_filter" : "filter_low_quality"
}


out = requests.get(URL, params = params)
all_data = []
data = out.json()
all_data.append(data)
# print data["paging"]
i=1
try:
    while "next" in data["paging"]:
        print "Request Number :", i
        # time.sleep(0.5)
        URL = data["paging"]["next"]
        out = requests.get(URL, params)
        data = out.json()
        all_data.append(data)
        # print data
        i += 1
        # if i==15:
        #     break


    with open('resultwef.json', 'w') as fp:
        json.dump(all_data, fp)

except Exception as e:
    print e
    with open('resulterr_filtered_wef.json', 'w') as fp:
        json.dump(all_data, fp)
