#!flask/bin/python
# Eclipse Public License 2.0

import requests
from utils import ConfigReader, PrintLog

# Mongo database handler, search and insert services
class Database():

    host = ''
    port = ''
    scheme = ''
    search_endpoint = ''
    insert_endpoint = ''
    status_endpoint = ''

    # Parse the config file
    def __init__(self):
        database_config = ConfigReader.read_config(section='database')
        self.host = database_config['host']
        self.port = database_config['port']
        self.scheme = database_config['scheme']
        self.insert_endpoint = database_config['insert_endpoint']
        self.search_endpoint = database_config['search_endpoint']
        self.status_endpoint = database_config['status_endpoint']
        self.database_endpoint = f'{self.scheme}://{self.host}:{self.port}'

        # if the database is not available, raise an error
        if self._get_status() is None:
            raise Exception('[Database] Error: Database is not available')

    
    # check status of the database?
    def _get_status(self):
        return self._get(self.status_endpoint, None)


    # Get handler
    def _get(self, endpoint, data):
        try:
            res = requests.get(self.database_endpoint + endpoint, json = data)
            # handle error codes
            if res.status_code != 200:
                raise Exception(f'[Database] Error: {res.status_code}')
            return res
        except Exception as error:
            PrintLog.log(error)
            return None
    
    # Post handler
    def _post(self, endpoint, data):
        try:
            res = requests.post(self.database_endpoint + endpoint, json = data)
            # handle error codes
            if res.status_code != 200:
                PrintLog.log(f'[Database] Error: {res.status_code}')                
            return res
        except Exception as err:
            PrintLog.log(err)
            return None

    # Insert a service
    def insert_service(self, data):
        return self._post(self.insert_endpoint, data)

    # Search for a service
    def search_service(self, data):
        return self._post(self.search_endpoint, data)
    