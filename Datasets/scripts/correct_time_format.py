import json
import iso8601
import datetime

comments = []

with open("./resultwef.json", 'r') as json_data:
    data = json.load(json_data)
    print len(data)

for ele in data:
    if "data" in ele:
        for com in ele["data"]:
            # dt = iso8601.parse_date(com["created_time"])
            comment = {
                "time" : com["created_time"],
                "message" : com["message"]
            }
            comments.append(comment)

print len(comments)
comments = sorted(comments, key = lambda x: iso8601.parse_date(x["time"]))
with open('corrected_data_wef.json', 'w') as fp:
    json.dump(comments, fp)
