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
from utils import ConfigReader, PrintLog


class ClassifyServices:

    # Parse the config file
    def __init__(self):
        dle_config = ConfigReader.read_config(section="dle")

        self.scheme = dle_config["scheme"]
        self.host = dle_config["host"]
        self.endpoint = dle_config["endpoint"]
        # Port 80, 443?
        if dle_config.get('port'):
            self.port = dle_config["port"]
            self.dle_uri = f"{self.scheme}://{self.host}:{self.port}"
        else:
            self.dle_uri = f"{self.scheme}://{self.host}"

    # Post handler
    def _post(self, endpoint, data):
        try:
            res = requests.post(
                self.dle_uri + endpoint, json=data
            )
            return res.json()
        except Exception as error:
            PrintLog.log(f"[ClassifyService] Error in post(): {str(error)}")
            return None

    def classify_services(self, data_dict):
        PrintLog.log("[ClassifyServices] Classify Services started.")
        # check if data_dict is a list of dicts
        if type(data_dict) is dict:
            # if is dict, convert to list
            data_dict = [data_dict]

        # build the request data
        for data in data_dict:
            dle_data = {
                "service_id": 34333,
                "service_name": data["name"],
                "service_desc": data["description"],
                "method": "Default"
            }
            res_json = self._post(self.endpoint, dle_data)
            if res_json is None:
                PrintLog.log("[ClassifyServices] Error in classify_services()")
                continue
            # update the service data with the classification result, the result is a list of keywords
            data["keywords"] = [res_json["service_class"][0]] + data["keywords"]

        PrintLog.log("[ClassifyServices] Classify Services ended.")
        return data_dict
