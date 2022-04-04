#!/usr/bin/python3
# Eclipse Public License 2.0

# Classification data demo - POST TO DLE API

from traceback import print_tb
import requests

demo_json = """
{
    "service_id":  34333,
    "service_name": " TransLoc openAPI",
    "method":  "Default",
    "service_desc": "The TransLoc OpenAPI is a public RESTful API which allows developers to access real-time vehicle tracking information and incorporate this data into their website or mobile application."
}
"""
url = 'http://smartclide.ddns.net:5001'
uri = f'{url}/smartclide/v1/dle/serviceclassification'

res = requests.post(uri, json = demo_json) # demo_json2
print(res, end='\n\n')
print(res.json())
