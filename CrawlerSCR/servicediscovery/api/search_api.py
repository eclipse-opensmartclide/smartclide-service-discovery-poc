#!flask/bin/python
# Eclipse Public License 2.0

from flask import request
from flask_restx import Resource

from servicediscovery.api.v1 import api
from servicediscovery.core import cache, limiter
from servicediscovery.elastic.elasticsearch import Elastic

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
          
            # validate data
            if 'query' not in data:
                return {'message': 'Missing query'}, 400
            

            l_elastic = Elastic()
            return  l_elastic.search(data)
