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

from datetime import datetime, time
import requests
import logging
from configparser import ConfigParser

# User-Agents are randomized per-session or per-request.
#  a random User-Agent is selected from the list useragents.txt (inside the requests_random_user_agent package)
import requests_random_user_agent


class ConfigReader():
    def read_config(section, filename='config.ini'):
        """
        Function for parsing the configuration file of the elasticsearch
        """
        parser = ConfigParser()
        parser.read(filename)

        if not parser.has_section(section):
            # Raise an exception to stop the execution
            raise Exception(
                'Section {0} not found in the {1} file'.format(section, filename))

        params = parser.items(section)
        return {param[0]: param[1] for param in params}


class PrintLog():
    def log(text):
        """
        Using logging and print for log the text recived as argument.
        """
        print(text)
        logging.info(text)


class SCRUtils():
    # Service code repo utils
    def get_url(url, header):
        """
        Function request get a url with a custom header, also handles error codes.
        """
        # TODO: handle more error codes!!
        response = requests.request("GET", url, headers=header)

        # TODO: handle posible infinite loop
        while (response.status_code == 429):  # Error API limit reached ?
            print("\nRateLimitExceededException")
            print("Sleeping (60s)")
            time.sleep(60)
            # Check again
            response = requests.request("GET", url, headers=header)

        return response

    def export_csv(data, name, export_index, export_header):
        """
        Function to export a DataFrame in the path, with a name + timestamp, and export index and/or header
        """
        path = "./output/"
        # data is a json, covert to pandas dataframe
        data.to_csv(path + name + '_' + datetime.now().strftime('%d_%m_%Y') + '.csv',
                    index=export_index,
                    header=export_header)


class FlaskUtils():

    def handle200error(self, message):
        """
        Function to handle 200 response
        """
        return message.json()

    def handle400error(self, message):
        """
        Function to handle a 400 (bad arguments code) error.
        """
        return self.abort(400, status=message, statusCode="400")

    def handle404error(self, message):
        """
        Function to handle a 404 (not found) error.
        """
        return self.abort(404, status=message, statusCode="404")

    def handle503error(self, message):
        """
        Function to handle a 503 (Service Unavailable ) error.
        """
        return self.abort(503, status=message, statusCode="503")

    def handle500error(self, message=None):
        """
        Function to handle a 500 (unknown) error.
        """
        if message is None:
            message = "Unknown error, please contact administrator."

        return self.abort(500, status=message, statusCode="500")
