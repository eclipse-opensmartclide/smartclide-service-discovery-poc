#!flask/bin/python
# Eclipse Public License 2.0

import json
from flask import request
from flask_restx import Resource

from api.v1 import api
from core import cache, limiter
from elastic.elasticsearch import Elastic

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

            try:
                json.loads(data)
            except TypeError:
                return 'Invalid parameter format, only JSON is acepted', 400

            if data is None:
                return {'message': 'Empty POST content'}, 400
            
            # The validation is done in the Elastic class
            l_elastic = Elastic()
            return  l_elastic.search(data)
