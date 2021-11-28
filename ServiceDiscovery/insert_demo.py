#!/usr/bin/python3
# Eclipse Public License 2.0

# Insert data in Elastic - POST Service Discovery API

import uuid
import requests

demo_json = {
    "full_name": {
        "0": "1337 / demo-leet"
    },
    "description": {
        "0": "Random service for the demo"
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
        "0": "demo,demo"
    },
    "source": {
        "0": "SmartCLIDE"
    },
    "uuid": {
        "0": str(uuid.uuid4())
    }
}



head_nocache = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

url = 'url'
uri = url + '/servicediscovery/v1/service_insert'

res = requests.post(uri, json = demo_json, headers= head_nocache) # demo_json2
if res.ok:
    print(res.json())
