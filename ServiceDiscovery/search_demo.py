#!/usr/bin/python3
# Eclipse Public License 2.0

# Search data in Elastic - POST Service Discovery API

import requests
import json

demo_json = {
    "full_name": {
        "0": "Dabm"
    },
    "description": {
        "0": "Random service for search"
    }
}

url = 'url'
uri = url + '/servicediscovery/v1/service_search'

res = requests.post(uri, json = demo_json) # demo_json2
if res.ok:
    print(res.json())
