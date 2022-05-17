#!flask/bin/python
# Eclipse Public License 2.0

from flask import request
from flask_restx import Resource
from api.api import api
from core import cache, limiter
from utils import PrintLog, FlaskUtils, ConfigReader

import requests
from database.database_handler import Database
from api.service_discovery_models import service_search_model

search_ns = api.namespace('service_search', description='Search for a service in the SmartCLIDE registry')
@search_ns.route('', methods = ['POST']) # url/user

class GetStatus(Resource):
    @limiter.limit('1000/hour')
    @api.expect(service_search_model)
    @cache.cached(timeout=1, query_string=True)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    @api.response(503, 'Service Unavailable')
    def post(self):

        if (data := request.get_json()) is None:                
            FlaskUtils.handle400error(search_ns, "Empty POST data")

        # new database handler
        try:
            db = Database()
        except Exception as err:
            FlaskUtils.handle500error(search_ns, "Search Service is unavailable, check the database configuration")

        # Data basic validation
        # Check if we have full_name, method and description, keywords is optional
        if 'full_name' not in data or 'description' not in data or 'keywords' not in data:
            FlaskUtils.handle400error(search_ns, "Missing parameters, case sensitive")

        # Check if the are empty
        if data['full_name'] == '' or data['description'] == '':
            FlaskUtils.handle400error(search_ns, "full_name and description data is required.")

        # if keyword is empty, call the DLE endpoint
        if data['keywords'] == '':
            PrintLog.log('[Search Service] Query keyword is empty, calling DLE service classification.')
            service = {
                "service_id": "1337",
                "method": "Default",
                "service_name": data['full_name'],
                "service_desc": data['description']            
            }
            dle_config = ConfigReader.read_config(section='dle')
            dle_endpoint = dle_config['scheme'] + '://' + dle_config['host'] + ':' + dle_config['port'] + dle_config['endpoint']
            try:
                response = requests.post(dle_endpoint, json=service)
            except Exception as err:
                FlaskUtils.handle500error(search_ns, "DLE service is unavailable, check the configuration or specify a keyword")
            # Valid response from service classification?
            if response.ok:
                data['keywords'] = response.json()['service_class']     

        # The actual search
        try:
            PrintLog.log(f'[Service Search] Searching for service: {data}')
            return db.search_service(data)
            
        except Exception as err:
           FlaskUtils.handle500error(search_ns, "Search Service is unavailable, check the database configuration")
