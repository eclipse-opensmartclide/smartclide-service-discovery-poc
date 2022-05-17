#!/usr/bin/python3
# Eclipse Public License 2.0

# Search data in Elastic - POST Service Discovery API

import requests
import json

demo_dictionary = {
    "full_name": "django",    
    "description":  "API support for Django REST framework",   
    # if the keyword is empty, the DLE classifier will generate a keyword based on the description and name
    "keywords":  "",
    }

url = 'http://localhost:2020'
uri = f'{url}/servicediscovery/v1/service_search'

res = requests.post(uri, json = demo_dictionary)
print(res, end='\n\n')
print(res.json())

