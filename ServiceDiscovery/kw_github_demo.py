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

# Remote call
import requests
import json
import pandas as pd
import concurrent.futures
import datetime


class RemoteKWGithub:
    def get_keywords(self, file):
        # Initial var
        with open(f"{file}") as f:
            keywords = [line.rstrip('\n').lower() for line in f]
        return keywords

    def call_api(self, kw):
        if not kw:
            return pd.DataFrame()
        get_params = {'from_keyword': kw}
        # Todo handle error codes
        response = requests.get(
            "http://localhost:2020/scr/v1/crawl_github", params=get_params)
        a_json = json.loads(response.text)
        return pd.DataFrame.from_dict(a_json)

    def remote_github_kw_from_file(self, file_name):
        keywords = self.get_keywords(file_name)
        tasks = []
        data = pd.DataFrame()
        # Iterate keywords on threads
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            for line in keywords:
                print("Task submited")
                tasks.append(executor.submit(self.call_api, line))

    # Iterate results
            print("Union results")
            # Todo union the dataframe generated in the API call
            for result in concurrent.futures.as_completed(tasks):
                data = data.append(result.result(), ignore_index=True)

        return data


if __name__ == '__main__':
    githubia = RemoteKWGithub()
    data = githubia.remote_github_kw_from_file("test.txt")
    print(data)
    # Export to csv
    data.to_csv("./" + "merged" + '_' +
                datetime.now().strftime('%d_%m_%Y') + '.csv',	index=True,	header=True)
