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

import requests
import dateutil.parser as parser
import dateutil.tz as tz

# Own
from utils import ConfigReader, PrintLog

# Database handler, search and insert services
class Database():

    host = ''
    scheme = ''
    registry_endpoint = ''
    services_endpoint = ''
    header = ''
  
    # Parse the config file
    def __init__(self):
        database_config = ConfigReader.read_config(section='database')
        self.scheme = database_config['scheme']
        self.host = database_config['host']
        self.header = {'Authorization': f"Bearer {database_config['token']}"}
        self.registry_endpoint = database_config['registry_endpoint']
        self.services_endpoint = database_config['services_endpoint']
        self.database_endpoint = f'{self.scheme}://{self.host}'

    # Get handler
    def _get(self, endpoint, data):
        try:                      
            res = requests.get(self.database_endpoint + endpoint, headers=self.header, json = data)        
            if res.status_code < 199 and res.status_code > 300:
                raise Exception(f'{res}')
            return res
        except Exception as error:
            PrintLog.log(f'[Database] Error in get(): {str(error)}')
            return None
    
    # Post handler
    def _post(self, endpoint, data):
        try:
            res = requests.post(self.database_endpoint + endpoint, headers=self.header, json=data)            
            if res.status_code < 199 and res.status_code > 300:
                raise Exception(f'{res}')
            return res
        except Exception as error:
            PrintLog.log(f'[Database] Error in post(): {str(error)}')
            return None

    # Insert a service, data is a list of json objects
    def insert_service(self, data):
        # for each service insert it in the database
        for service in data:
            # set dates to iso format
            try:
                service['created'] = parser.parse(service['created']).replace(tzinfo=tz.gettz('UTC')).isoformat()
            except:
                service['created'] = ""
            try:
                service['updated'] = parser.parse(service['updated']).replace(tzinfo=tz.gettz('UTC')).isoformat()  
            except:
                service['updated'] = ""
                         
            # keywords to list
            keywords = service['keywords']
            if keywords is not None:
                keywords = keywords.split(',')
                service['keywords'] = keywords
            else:
                service['keywords'] = []
    
            res = self._post(self.services_endpoint, service)  
        # for end          
        return res
        #return self._post(self.services_endpoint, data)
    
    def get_service_registries(self):
        return self._get(self.registry_endpoint, None)

    def get_service_registry(self, registry_id):
        return self._get(f'{self.registry_endpoint}/{registry_id}', None)    

    def post_service_registry(self, data):
        return self._post(self.registry_endpoint, data)
    
    def get_services(self, data):
        return self._get(self.services_endpoint, data)

    def get_service(self, service_id):
        return self._get(f'{self.services_endpoint}/{service_id}', None)
    