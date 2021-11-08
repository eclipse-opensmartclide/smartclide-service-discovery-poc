#!/usr/bin/python3
# Eclipse Public License 2.0

# Insert data. POST

import requests

demo_json = """
{
    "full_name": {
        "0": "1337 / demo-leet"
    },
    "link": {
        "0": "https://url.com/1337/demo-leet"
    },
    "description": {
        "0": "Random service for the demo"
    },
    "updated_on": {
        "0": "2021-10-10 15:00:00"
    },
    "keywords": {
        "0": "demo,demo"
    },
    "source": {
        "0": "SmartCLIDE"
    }
}
"""
demo_json2 = """
{
    "full_name": {
        "0": "bigInt / demo"
    },
    "link": {
        "0": "https://url2.com/bigInt/demo"
    },
    "description": {
        "0": "Another random service for the demo"
    },
    "updated_on": {
        "0": "2021-10-10 16:00:00"
    },
    "keywords": {
        "0": "demo-two"
    },
    "source": {
        "0": "SmartCLIDE"
    }
}
"""
head_nocache = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

uri = 'URI/scr/v1/service_insert'

res = requests.post(uri, json = demo_json, headers= head_nocache) # demo_json2
if res.ok:
    print(res.json())
