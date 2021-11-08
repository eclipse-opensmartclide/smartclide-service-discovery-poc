#!flask/bin/python
# Eclipse Public License 2.0

#!flask/bin/python
# Eclipse Public License 2.0

import json
import re
from elasticsearch import Elasticsearch
import pandas as pd

from flask import request
from flask_restx import Resource
from scr.api.v1 import api
from scr.core import cache, limiter
from scr.utils import FlaskUtils

search_ns = api.namespace('service_search', description='Search for a service in the registry')
@search_ns.route('', methods = ['POST']) # url/user
class GetStatus(Resource):
    @limiter.limit('1000/hour')
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    def post(self):
        if request.method == 'POST':
            data = request.json
   
            # Normalize json
            json_data = json.loads(data)
            
            # To daraframe
            dataframe = pd.DataFrame.from_dict(json_data)
            
            # Build query
            query = dataframe["full_name"][0] + " OR "+  dataframe["description"][0] + " OR " + dataframe["keywords"][0]
            
            query_body ={
                "query": {
                    "query_string" : {
                    "fields" : ["description", "full_name", "keywords"],
                    "query" : query,
                    }
                }
            }
            
            # TODO read from database.ini
            remote_elastic = ''
            elastic_client = Elasticsearch(hosts=[remote_elastic])

            # The actual search
            result = elastic_client.search(index="scr", body=query_body)

            # Hits
            all_hits = result['hits']['hits']

            # No hits?
            if all_hits == []:
                return {"0" :"No services have been found for that query. The Crawler subcomponent will search for it. Try again later."}

            # We have hits!
            # Iterate the nested dictionaries inside the ["hits"]["hits"] list
            hits = []
            for num, doc in enumerate(all_hits):
                print("DOC ID:", doc["_id"], "\n\n", doc, "\n")
                hits.append(json.dumps(doc))
                
            return json.dumps(hits)
