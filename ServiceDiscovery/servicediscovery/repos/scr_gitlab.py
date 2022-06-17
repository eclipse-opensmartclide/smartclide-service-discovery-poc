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

import time
import random
import re
import uuid

# own
from utils import SCRUtils, PrintLog
from database.database_handler import Database
from repos.clean_data import ServiceCrawledDataPreProcess

class CrawlerGitLab:

    preprocess = ServiceCrawledDataPreProcess()

    # constructor
    def __init__(self, ptoken):
        """
        Creates an isntance of CrawlerGitLab using the ptoken argument.
        """
        self.token = ptoken

    def get_from_url(self, url):
        """
        Parses the URL given to search for repositories in GitLab.
        """
        # find all the text bwt / and get the last [-1] 
        # https://gitlab.com/dabm-git/ --> [https:] [gitlab.com] [dabm-git]
        username = re.findall("([^\/]+)", url)[-1]
        return self.get_repos(payload = username, from_url = True)

    def get_from_keywords(self, keywords):
        """
        Parses the keywords given to search for repositories in GitLab.
        """   
        # Split the search keywords in case of multiple
        keywords = [keyword.strip() for keyword in keywords.split(',')]
        # Make sure we have valid keywords names
        # [^A-Za-z0-9+]+
        keywords = [re.sub('[^A-Za-z0-9+]+', '', key) for key in keywords]        
        keywords = '+'.join(keywords)

        return self.get_repos(payload = keywords, from_keywords = True)

    def get_repos(self, payload, from_url = False, from_keywords = False):
        """
        Search for repositories in GitLab based on the payload given and the type of search,
        from URL or Keyword using get requests on its API.
        The result is exported to .csv files and then loaded into a Postgre database. 
        """ 
        # Initial
        page = 1
        data = []
        url = ""
        w_flag = True

        PrintLog.log(f"[GitLab] Get repos started: {payload}")

        # Iterate pages
        while w_flag:
            if from_url:
                # https://docs.gitlab.com/ee/api/projects.html          
                url = f"https://gitlab.com/api/v4/users/{payload}/projects?simple=1&per_page=100&page={page}"
            if from_keywords:
                # https://docs.gitlab.com/ee/api/search.html
                url = f"https://gitlab.com/api/v4/search?scope=projects&search={payload}&per_page=100&page={page}"

            # GitLab API v4 "Bearer + token"
            # TODO: handle more API tokens in case of limit
            header = {'Authorization': f"Bearer {self.token}"}

            response = SCRUtils.get_url(url, header)

            if response.status_code < 200 or response.status_code >= 300:
                PrintLog.log(f"[GitLab] Error: {response.status_code}, Bad creditentials? Check the token.")
                raise Exception("Bad Creditentials")

            headers = response.headers # Next-Page
            response_json = response.json()

            # Iterate all repos in jsons
            for repo in response_json:
                # Response fix
                if not isinstance(repo, dict):                    
                    continue

                # Make sure we dont have KeyError
                # TODO, GET /projects/:id/languages %

                description = ""
                if(repo['description'] is not None):
                    description = " ".join(re.split("\s+", repo['description'])) # remplace with spaces " "
                if('path' not in repo): repo['path'] = ""
                if('last_activity_at' not in repo): repo['last_activity_at'] = ""
                if('created_at' not in repo): repo['created_at'] = ""
                if('topics' not in repo): repo['topics'] = ""
                if('web_url' not in repo): repo['web_url'] = ""
                if('star_count' not in repo): repo['star_count'] = ""
                if('forks_count' not in repo): repo['forks_count'] = ""
                if('license' not in repo): 
                    repo['license'] = {}
                    repo['license']['name'] = ""

                # If we have more tags, merge them with the current kw
                merged_kw = payload.replace("+",",")
                if repo['topics']:
                    repo_tags = ','.join(repo['topics'])
                    merged_kw = f"{merged_kw},{repo_tags}"               

                # Create json repo
                datarepo = {
                    "id" : str(uuid.uuid4()),
                    "name": repo['path'],  
                    "user_id": "ee123203cb634a4eb9edd7ec582d099f",
                    "registry_id": "bb123213ad223a45ba1d7sdc582d055e",
                    "git_credentials_id": "628c922780b42501489a85dd",
                    "url": repo['web_url'],
                    "description": description,
                    "is_public": True,
                    "licence": repo['license']['name'],
                    "framework": "",
                    "created": repo['created_at'],
                    "updated": repo['last_activity_at'],
                    "stars": repo['star_count'],                 
                    "forks": repo['forks_count'],
                    "watchers": "0",
                    "deployable": False, #TODO: check if deployable     
                    "keywords": merged_kw,        
                }
                # Add json to data list
                data.append(datarepo)
                # Random delay to avoid requests timeout
                time.sleep(random.uniform(0.1, 0.3))

            # More pages with same keyword?
            if ('X-Next-Page' not in headers) or not headers['X-Next-Page']:
                w_flag = False
            else:
                page += 1

        # While ended, export to csv and load into database
        if not data:
            PrintLog.log("[GitLab] No valid repos found for the given input.")  
            return {} # empty

        file_name = "GitLab_"
        if from_url:
            file_name = "GitLab_url_"
        if from_keywords:
            file_name = "GitLab_kw_"

        # Clean
        data_cleaned = self.preprocess.clean_export_data(data, file_name + payload)
     
        # at this point we have some data, so we can upload it to the database
        try:
            PrintLog.log(f"[GitLab] Upload to database called from GitLab crawler")
            _ = Database().insert_service(data_cleaned)
        except Exception as e:
            PrintLog.log(f"[GitLab] Error while inserting data into database: {e}")

        return data_cleaned


        

       