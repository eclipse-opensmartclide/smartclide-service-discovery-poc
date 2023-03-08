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
import pandas as pd

# Own
from utils import ConfigReader, PrintLog, SCRUtils
from .serviceclassification import ClassifyServices


class Database:

    ClassifyService = ClassifyServices()

    # Parse the config file
    def __init__(self):
        database_config = ConfigReader.read_config(section="database")
        self.scheme = database_config["scheme"]
        self.host = database_config["host"]
        if database_config.get('token'):
            self.header = {
                "Authorization": f"Bearer {database_config['token']}"}
        else:
            self.header = ""
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
                raise Exception(f"{res}")  # Specific exception?
            return res
        except Exception as error:
            PrintLog.log(f"[Database] Error in get(): {str(error)}")
            return None

    # Post handler
    def _post(self, endpoint, data):
        try:
            return requests.post(
                self.database_endpoint + endpoint, headers=self.header, json=data
            )
        except Exception as error:
            PrintLog.log(f"[Database] Error in post(): {str(error)}")
            return None
    def export_crawled_data(self,data_list, file_name):
        # convert the list data_list to dataframe
        df = pd.DataFrame(data_list, columns=[
            "id",
            "name",
            "user_id",
            "registry_id",
            "git_credentials_id",
            "url",
            "description",
            "is_public",
            "licence",
            "framework",
            "created",
            "updated",
            "stars",
            "forks",
            "watchers",
            "deployable",
            "keywords",
        ])
        # Export the dataframe to csv file
        SCRUtils.export_csv(df, file_name, True, True)
    # Insert a service, data is a list of dict
    def insert_service(self, data, name):
        # call the DLE class service
        data_classified = self.ClassifyService.classify_services(data)
        self.export_crawled_data(data_classified, name)
        return self._post(self.services_endpoint, data_classified)

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
