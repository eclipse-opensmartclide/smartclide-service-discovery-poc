#!/usr/bin/python3
# Eclipse Public License 2.0

# Insert data in Elastic - POST Service Discovery API

import uuid
import requests
import json

demo_json ={
    "full_name": {
        "0": "insert-demo"
    },
    "description": {
        "0": "Random service insert for the demo"
    },
    "link": {
        "0": "https://url.com/1337/demo-leet"
    },
    "stars": {
        "0": "0"
    },
    "forks": {
        "0": "0"
    },
    "watchers": {
        "0": "0"
    },
    "updated_on": {
        "0": "0"
    },
    "keywords": {
        "0": "demo"
    },
    "source": {
        "0": "SmartCLIDE"
    },
    "uuid": {
        "0": str(uuid.uuid4())
    }
}

# convert demo_json to json
json_data = json.dumps(demo_json)

# convet  demo_json to dataframe
head_nocache = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

url = 'http://18.185.35.23:2020'
uri = url + '/servicediscovery/v1/service_insert'

res = requests.post(uri, json = json_data, headers= head_nocache) # demo_json2
print(res.json())
