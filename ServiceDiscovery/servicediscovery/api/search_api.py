#*******************************************************************************
# Copyright (C) 2022 AIR Institute
# 
# This program and the accompanying materials are made
# available under the terms of the Eclipse Public License 2.0
# which is available at https://www.eclipse.org/legal/epl-2.0/
# 
# SPDX-License-Identifier: EPL-2.0
# 
# Contributors:
#    David Berrocal Macías (@dabm-git) - initial API and implementation
#*******************************************************************************

from flask import request
from flask_restx import Resource
from api.api import api
from core import cache, limiter
from utils import PrintLog, FlaskUtils, ConfigReader

import requests
from database.database_handler import Database
from api.service_discovery_models import service_search_model, service_search_model_example

search_ns = api.namespace('service_search', description='Search for a service in the SmartCLIDE registry')
@search_ns.route('', methods = ['POST']) # url/user

class GetStatus(Resource):
    @limiter.limit('1000/hour')
    @api.marshal_with(service_search_model_example, code=200, description='OK', as_list=False)
    @api.expect(service_search_model)
    @cache.cached(timeout=1, query_string=True)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    @api.response(503, 'Service Unavailable')
    def post(self):
        # get data from POST
        if (data := request.get_json()) is None:                
            FlaskUtils.handle400error(search_ns, "Empty POST data")

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
            except Exception as e:
                PrintLog.log('[Search Service] DLE service is unavailable.')
                # DLE service is unavailable, assume the service has a generic keyword
                
            data['keywords'] = 'Generic Service'
            # Valid response from service classification?
            if response.ok:
                data['keywords'] = response.json()['service_class']
            else:
                PrintLog.log('[Search Service] DLE service is unavailable.')
  
        # The actual search
        try:
            PrintLog.log(f'[Search Service] Searching for service:\n{data}')
            return Database().search_service(data)
        except Exception as _:
            FlaskUtils.handle500error(search_ns, "Search Service is unavailable")
