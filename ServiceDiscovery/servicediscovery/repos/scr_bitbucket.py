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
import re
import random
from bs4 import BeautifulSoup
import uuid

# own
from utils import SCRUtils, PrintLog
from repos.clean_data import ServiceCrawledDataPreProcess
from database.database_handler import Database

class CrawlerBitbucket:
    preprocess = ServiceCrawledDataPreProcess()

    # Constructor
    def __init__(self):
        """
        Creates an isntance of CrawlerBitbucket using the ptoken argument.
        """
        #self.token = ptoken
        pass

    # WIP    
    def get_from_url_API(self, url):
        None
        # Example multiple pages: https://bitbucket.org/atlassian_tutorial/ 
        # https://api.bitbucket.org/2.0/repositories/atlassian_tutorial/
        #   find next: https://api.bitbucket.org/2.0/repositories/atlassian_tutorial?page=2
        #user_org = "atlassian_tutorial"  
        #header = {'Authorization': "Bearer " + self.token}
        #next_page_url = 'https://api.bitbucket.org/2.0/repositories/%s?pagelen=10&fields=next,values.links.clone.href,values.slug' % user_org
        
        # Parse repositories from the JSON
        #while next_page_url is not None:
        #    response = SCRUtils.get_url(next_page_url, header=header)
        #    page_json = response.json()            
        #    print(page_json)        
            # handle more API tokens in case of limit
            #for repo in page_json['values']:
            #    reponame=repo['slug']
            #    repohttp=repo['links']['clone'][0]['href'].replace('SaravThangaraj@','')
            #    repogit=repo['links']['clone'][1]['href']
            #
            #    print(reponame+","+repohttp+","+repogit)
            #    #full_repo_list.append(repo['slug'])
            
            # Get the next page URL, if present
            # It will include same query parameters, so no need to append them again
            #next_page_url = page_json.get('next', None)
    

    def get_num_pages_repo_web(self, keyword):
        """
        Function to get the number of pages of the repository in the bitbucket search engine for a keyword given.
        """  
        url = f"https://bitbucket.org/repo/all/1?name={keyword}"
        response = SCRUtils.get_url(url, header="")

        # Get num pages        
        soup = BeautifulSoup(response.text, 'lxml')
        aui_item = soup.find("section", {"class": "aui-item"})
        title = aui_item.find("h1")  # Find title
        number_regex = re.compile(r'-?\d+(?:\.\d+)?')
        numbers = number_regex.findall(title.text)

        return (int(numbers[0]) // 10) + 1
    
    # Web search engine based
    def get_from_keywords_web(self, keywords):
        """
        Search for repositories in BitBucket using get requests based on the keywords given.
        The result is exported to .csv files and then loaded into a database. 
        """ 

        PrintLog.log(f"[BitBucket] Get repos started: {keywords}")

        # https://support.atlassian.com/bitbucket-cloud/docs/api-request-limits/
        # Git web (HTTPS://) requests           60,000 requests per hour
        # Any access to /2.0/repositories/*     1,000 per hour

        # Split the search keywords in case of multiple
        keyword_split = [keyword.strip() for keyword in keywords.split(',')]
        # Make sure we have valid keywords names
        # [^A-Za-z0-9+]+
        keyword_split = [re.sub('[^A-Za-z0-9+]+', '', key) for key in keyword_split]
        keyword_split = ','.join(keyword_split)

        data = []
        max_pages = self.get_num_pages_repo_web(keyword_split)

        # Iterate pages, start at 1
        for page in range(1, max_pages + 1):

            url = f"https://bitbucket.org/repo/all/{str(page)}?name={keyword_split}"            
            response = SCRUtils.get_url(url, header="")

            # Find repos
            soup = BeautifulSoup(response.text, 'lxml')
            repo_summary = soup.find_all("article", {"class": "repo-summary"})

            for repo in repo_summary:
                # Get info from repo
                repo_metadata = repo.find('ul', {"class": "repo-metadata clearfix"})
                repo_metadata_li = repo_metadata.find_all('li')

                # Get description
                try:
                    description = repo.find('p').text
                    # Clean ('description')
                    description = description.replace("\',)", "")
                    description = description.replace("(\'", "")
                except AttributeError:
                    description = ""

                # json datarepo
                datarepo = {
                        "id" : str(uuid.uuid4()),
                        "name": repo.find('a', {"class": "repo-link"}, href=True).text, # get repo name,  
                        "user_id": "628c87f6aa5a2857398a80a0", # cte
                        "registry_id": "628c8dab80b42501489a85da", # cte
                        "git_credentials_id": "628c922780b42501489a85dd",
                        "url": "https://bitbucket.org" + repo.find('a', {"class": "repo-link"}, href=True)['href'],  
                        "description": description,
                        "is_public": True,
                        "licence": "",
                        "framework": "",
                        "created": "",
                        "updated": repo_metadata_li[1].find('time')['datetime'],
                        "stars": '0',
                        "forks": '0',
                        "watchers":  repo_metadata_li[0].find('a').text.strip().replace(" watchers", "").replace(" watcher", ""),
                        "deployable": False,# TODO: check if deployable 
                        "keywords": keyword_split,
                }
                # Append repo
                data.append(datarepo)
            # Since we use web requests it is good to wait between requests to avoid IP bans
            time.sleep(random.uniform(0.1, 0.4))
            # Repos in one page end
        # Max pages end
        # Create dataframe from json list & export one csv per keyword
        if not data:
            PrintLog.log("[BitBucket] No valid repos found for the given keywords.")  
            return {} # empty

        file_name = "Bitbucket_kw_"
        # Clean
        data_cleaned = self.preprocess.clean_export_data(data, file_name + keyword_split)

        # at this point we have some data, so we can upload it to the database
        try:
            PrintLog.log(f"[BitBucket] Upload to database called from BitBucket crawler")
            _ = Database().insert_service(data_cleaned)
        except Exception as e:
            PrintLog.log(f"[BitBucket] Error while inserting data into database: {e}")
        return data_cleaned
