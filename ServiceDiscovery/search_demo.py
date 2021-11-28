#!/usr/bin/python3
# Eclipse Public License 2.0

# Search data in Elastic - POST Service Discovery API

import requests
import json

demo_json ={
    "full_name": {
        "0": "django"
    },
    "description": {
        "0": "API support for Django REST framework"
    },
    "keyword": {
        "0": "django"
    }
}

json_data = json.dumps(demo_json)

url = 'http://18.185.35.23:2020'
uri = url + '/servicediscovery/v1/service_search'

res = requests.post(uri, json = json_data) # demo_json2
print(res.json())
