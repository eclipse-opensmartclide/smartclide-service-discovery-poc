#!flask/bin/python
# Eclipse Public License 2.0

from flask import request
from flask_restx import Resource

from api.v1 import api
from core import cache, limiter
from elastic.elasticsearch import Elastic
from utils import PrintLog, FlaskUtils

search_ns = api.namespace('service_search', description='Search for a service in the registry')
@search_ns.route('', methods = ['POST']) # url/user
class GetStatus(Resource):
    @limiter.limit('1000/hour')
    @cache.cached(timeout=1, query_string=True)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    @api.response(503, 'Service Unavailable')
    def post(self):
        if request.method != 'POST':
            return

        if (data := request.get_json()) is None:                
            FlaskUtils.handle400error(search_ns, "Empty POST data")

        try: 
            # If elasticsearch is not available, dont even try to build the query            
            srch = Elastic().search(data)
        except Exception as e:
            PrintLog.log("[service_search] Search service is unavailable, check the Elasticsearch status")               
            FlaskUtils.handle503error(search_ns, 'Search service is unavailable')
    
        return srch
