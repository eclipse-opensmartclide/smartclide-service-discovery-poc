# *******************************************************************************
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
# *******************************************************************************

import requests

# Own
from utils import ConfigReader, PrintLog

# Database handler, search and insert services
class Database:

    host = ""
    scheme = ""
    registry_endpoint = ""
    services_endpoint = ""
    header = ""

    # Parse the config file
    def __init__(self):
        database_config = ConfigReader.read_config(section="database")
        self.scheme = database_config["scheme"]
        self.host = database_config["host"]
        self.header = {"Authorization": f"Bearer {database_config['token']}"}
        self.registry_endpoint = database_config["registry_endpoint"]
        self.services_endpoint = database_config["services_endpoint"]
        self.database_endpoint = f"{self.scheme}://{self.host}"

    # Get handler
    def _get(self, endpoint, data):
        try:
            res = requests.get(
                self.database_endpoint + endpoint, headers=self.header, json=data
            )
            if res.status_code < 199 and res.status_code > 300:
                raise Exception(f"{res}")
            return res
        except Exception as error:
            PrintLog.log(f"[Database] Error in get(): {str(error)}")
            return None

    # Post handler
    def _post(self, endpoint, data):
        try:
            print(self.database_endpoint + endpoint)
            res = requests.post(
                self.database_endpoint + endpoint, headers=self.header, json=data
            )
            return res
        except Exception as error:
            PrintLog.log(f"[Database] Error in post(): {str(error)}")
            return None

    # Insert a service, data is a list of {}
    def insert_service(self, data):
        # open a local document for writing debug purposes
        # file = open('services.json', 'a+')
        # file.write(json.dumps(data))
        return self._post(self.services_endpoint, data)

    def get_service_registries(self):
        return self._get(self.registry_endpoint, None)

    def get_service_registry(self, registry_id):
        return self._get(f"{self.registry_endpoint}/{registry_id}", None)

    def post_service_registry(self, data):
        return self._post(self.registry_endpoint, data)

    def get_services(self, data):
        return self._get(self.services_endpoint, data)

    def get_service(self, service_id):
        return self._get(f"{self.services_endpoint}/{service_id}", None)
