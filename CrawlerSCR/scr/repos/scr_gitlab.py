#!/usr/bin/python3
# Eclipse Public License 2.0

import pandas as pd
import re

# own
from scr.utils import SCRUtils
from scr.postgresql.config import postgresql

class CrawlerGitLab:
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

        # Iterate pages
        while (w_flag):        
            if from_url:
                # https://docs.gitlab.com/ee/api/projects.html          
                url = f"https://gitlab.com/api/v4/users/{payload}/projects?simple=1&per_page=100&page={page}"
            if from_keywords:
                # https://docs.gitlab.com/ee/api/search.html
                url = f"https://gitlab.com/api/v4/search?scope=projects&search={payload}&per_page=100&page={page}"

            # GitLab API v4 "Bearer + token"
             # TODO: handle more API tokens in case of limit
            header = {'Authorization': "Bearer " + self.token}

            response = SCRUtils.get_url(url, header)
            headers = response.headers # Next-Page
            response_json = response.json()

            # Iterate all repos in jsons
            for repo in response_json:
                # Response fix
                if not isinstance(repo, dict):                    
                    continue

                # Make sure we dont have KeyError
                #if('id' not in repo): repo['id'] = ""
                     
                description = ""
                if(repo['description'] is not None):
                    description = " ".join(re.split("\s+", repo['description'])) # remplace with spaces " "
                if('path' not in repo): repo['path'] = ""
                if('last_activity_at' not in repo): repo['last_activity_at'] = ""                         
                if('tag_list' not in repo): repo['tag_list'] = ""            
                if('web_url' not in repo): repo['web_url'] = ""   
                if('star_count' not in repo): repo['star_count'] = ""
                if('forks_count' not in repo): repo['forks_count'] = ""

                # If we have more tags, merge them with the current kw
                merged_kw = payload.replace("+",",")        
                if repo['tag_list']:
                    repo_tags = ','.join(repo['tag_list'])                  
                    merged_kw = merged_kw + "," + repo_tags                

                # Create json repo
                datarepo = {
                    "full_name": repo['path'],  
                    "description": description,                    
                    "link": repo['web_url'],
                    "stars": repo['star_count'],                 
                    "forks": repo['forks_count'],
                    "watchers": "-1",           
                    "updated_on": repo['last_activity_at'],
                    #"id": repo['id'],
                    "keywords": merged_kw,
                    "source": "GitLab"
                }

                # Add json to data list
                data.append(datarepo)

            # More pages with same keyword?
            if ('X-Next-Page' not in headers) or not headers['X-Next-Page']:
                w_flag = False
            else:
                page += 1
        
        # While end
        # Create dataframe from json list & export one csv per keyword
        df_gitlab = pd.json_normalize(data=data)
        df_gitlab.reset_index(drop=True, inplace=True)

        file_name = "GitLab_"
        if from_url:
            file_name = "GitLab_url_"
        if from_keywords:
            file_name = "GitLab_kw_"

        SCRUtils.export_csv(df_gitlab, "./output/", file_name + payload, True, True)
        
        # To postgresql
        #post = postgresql()
        #post.upload_to_db("scr", df_gitlab)
        
        return df_gitlab


        

       