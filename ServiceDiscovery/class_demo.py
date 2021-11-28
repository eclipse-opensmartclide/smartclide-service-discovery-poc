#!/usr/bin/python3
# Eclipse Public License 2.0

# Classification data demo - POST TO DLE API

import requests

demo_json = """
{
    "service_id":  34333,
    "service_name": " TransLoc openAPI",
    "service_desc": 
    "The TransLoc OpenAPI is a public RESTful API which allows developers to access real-time vehicle tracking information and incorporate this data into their website or mobile application."
}
"""

head_nocache = {
    "Cache-Control": "no-cache",
    "Pragma": "no-cache"
}

url = 'url'
uri = url + '/servicediscovery/v1/service_search'

res = requests.post(uri, json = demo_json, headers= head_nocache) # demo_json2
if res.ok:
    print(res.json())
