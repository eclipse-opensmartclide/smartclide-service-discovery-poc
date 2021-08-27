#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import Api
from flask_restx import Resource
from scr.core import cache, limiter

api = Api(version='1.0',
		  title='SCR project',
		  description="**SCR project's Flask RESTX API**")

## TODO: MB, handle satus for avoid abusive calls + report api tokens status
status_ns = api.namespace('status', description='Crawler status')
@status_ns.route('', methods = ['GET']) # url/user
class GetStatus(Resource):
    @limiter.limit('1000/hour') 
    @cache.cached(timeout=84600, query_string=True)   
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    def get(self):
    	return "TODO"