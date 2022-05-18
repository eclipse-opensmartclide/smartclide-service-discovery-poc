#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import Resource
from flask import request
import pandas as pd
import json
from api.api import api
from core import cache, limiter
from database.database_handler import Database
from utils import PrintLog, FlaskUtils
from api.service_discovery_models import service_insert_model, service_insert_model_example

insert_ns = api.namespace('service_insert', description='Insert a new service to the SmartCLIDE registry')

@insert_ns.route('', methods = ['POST']) # url/user
class GetStatus(Resource):
    @limiter.limit('1000/hour')
    @api.marshal_with(service_insert_model_example, code=200, description='OK', as_list=False)
    @api.expect(service_insert_model)
    @cache.cached(timeout=1, query_string=True)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    @api.response(503, 'Service Unavailable')
    def post(self): 
        # get data from POST
        if not (data := request.get_json()):
            FlaskUtils.handle400error(insert_ns, "Empty POST data")                

        # check if df have all the right columns
        if not {
            'full_name',
            'link',
            'stars',
            'forks',
            'watchers',
            'updated_on',
            'keywords',
            'source',
            'uuid',
        }.issubset(data):
            FlaskUtils.handle400error(insert_ns, "Invalid data format, the POST columns are not correct to perform an insertion.")

        # convert source content to lowercase
        data['source'] = data['source'].lower()

        # check if the source lowercase is github or bitbucket or gitlab
        if data['source'].lower() in ['github', 'bitbucket', 'gitlab']:
            FlaskUtils.handle400error(insert_ns, "Invalid data source, source must not be GitHub or Bitbucket or GitLab.")   

        # new database handler
        try:
            res =  Database().insert_service(data)
            PrintLog.log(f"[service_insert] Inserting new service to the SmartCLIDE registry:\n{data}")
            # export the json data to csv
            try:
                df = pd.DataFrame([data])
                df.to_csv('output/SmartCLIDE_insert_' + data['full_name'] + data['uuid'] + '.csv', index=False)
            except Exception as err:
                PrintLog.log(f"[service_insert] Error exporting the json data to csv: {str(err)}")

            if res.status_code == 200:
                FlaskUtils.handle200error(insert_ns, "Data inserted correctly")
        except Exception as err:
            FlaskUtils.handle400error(insert_ns, "Insert Service is unavailable.")

        
