#!flask/bin/python
# Eclipse Public License 2.0

from flask import request
from flask_restx import Resource
from scr.api.v1 import api
from scr.core import cache, limiter

from scr.elastic.elasticsearch import Elastic

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
            # Todo: validate data

            l_elastic = Elastic()
            return  l_elastic.search(data)
