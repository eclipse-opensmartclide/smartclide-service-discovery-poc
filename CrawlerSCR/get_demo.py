#!/usr/bin/python3
# Eclipse Public License 2.0

# Get data. POST

import requests
import json

demo_json = """
{
    "full_name": {
        "0": "Dabm"
    },
    "description": {
        "0": "Random service for the demo"
    },
    "keywords": {
        "0": "demo"
    }
}
"""

uri = 'URI'
#uri = 'URI'

res = requests.post(uri, json = demo_json) # demo_json2
if res.ok:
    print(res.json())
