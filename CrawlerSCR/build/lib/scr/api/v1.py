#!flask/bin/python
# Eclipse Public License 2.0


from flask_restx import Api
from flask_restx import Resource
from flask import request
from scr.core import cache, limiter

import pandas as pd
from io import StringIO

api = Api(version='1.0',
		  title='SCR project',
		  description="**SCR project's Flask RESTX API**")

insert_ns = api.namespace('service_insert', description='Insert a new service to the registry')
@insert_ns.route('', methods = ['POST']) # url/user
class GetStatus(Resource):
    @limiter.limit('1000/hour') 
    @cache.cached(timeout=84600, query_string=True)   
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    def post(self):
        if request.method == 'POST':
            content = request.json
            df = pd.read_json(StringIO(content))
            print(df)
            ## TODO> INSERT TO ELASTIC!
            return content
