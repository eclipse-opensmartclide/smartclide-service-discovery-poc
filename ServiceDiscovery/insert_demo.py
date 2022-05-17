#!/usr/bin/python3
# Eclipse Public License 2.0

# Insert data in Elastic - POST Service Discovery API

import uuid
import requests
import json

demo_dictionary = { "full_name": "insert-demo",
                    "description":  "Random service insert for the demo",
                    "link": "https://url.com/1337/demo-leet",
                    "stars":  "0",  
                    "forks": "0",
                    "watchers": "0",
                    "updated_on": "0",
                    "keywords": "demo",
                    "source": "SmartCLIDE_demo",   
                    "uuid":  str(uuid.uuid4())
                    }

url = 'http://localhost:2020'
uri = f'{url}/servicediscovery/v1/service_insert'

res = requests.post(uri, json = demo_dictionary)
print(res, end='\n\n')
print(res.json())
