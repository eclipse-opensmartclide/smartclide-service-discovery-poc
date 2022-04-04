#!/usr/bin/python3
# Eclipse Public License 2.0

# Search data in Elastic - POST Service Discovery API

import requests
import json

demo_dictionary = {
    "full_name": "django",    
    "description":  "API support for Django REST framework",   
    # if the keyword is not present, the DLE classifier generate a keyword based on the description
    "keywords":  ""
    }

demo_json = json.dumps(demo_dictionary)

url = 'http://localhost:2020'
uri = f'{url}/servicediscovery/v1/service_search'

res = requests.post(uri, json = demo_json)
print(res, end='\n\n')
print(res.json())

