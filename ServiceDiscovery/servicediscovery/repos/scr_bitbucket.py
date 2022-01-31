#!/usr/bin/python3
# Eclipse Public License 2.0

import time
import re
import pandas as pd
import random
from bs4 import BeautifulSoup
import uuid

# own
from servicediscovery.utils import SCRUtils, PrintLog
from servicediscovery.elastic.elasticsearch import Elastic
from servicediscovery.repos.clean_data import ServiceCrawledDataPreProcess

class CrawlerBitbucket:
    preprocess = ServiceCrawledDataPreProcess()
    elastic_end = Elastic()

    # Constructor
    def __init__(self, ptoken):
        """
        Creates an isntance of CrawlerBitbucket using the ptoken argument.
        """
        self.token = ptoken

    # WIP
    def get_from_url_API(self, url):
        # Example multiple pages: https://bitbucket.org/atlassian_tutorial/ 
        # https://api.bitbucket.org/2.0/repositories/atlassian_tutorial/
        #   find next: https://api.bitbucket.org/2.0/repositories/atlassian_tutorial?page=2
        user_org = "atlassian_tutorial"  
        header = {'Authorization': "Bearer " + self.token}
        next_page_url = 'https://api.bitbucket.org/2.0/repositories/%s?pagelen=10&fields=next,values.links.clone.href,values.slug' % user_org
        
        # Parse repositories from the JSON
        while next_page_url is not None:
            response = SCRUtils.get_url(next_page_url, header=header)
            page_json = response.json()            
            print(page_json)        
            # TODO: handle more API tokens in case of limit
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
        The result is exported to .csv files and then loaded into a Postgre database. 
        """ 

        PrintLog.log("Get BitBucket repos started: " + keywords)

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
                
                # Todo: handle empty
                # json datarepo
                datarepo = {
                    "full_name": repo.find('a', {"class": "repo-link"}, href=True).text, # get repo name
                    "description": description,
                    "link": "https://bitbucket.org" + repo.find('a', {"class": "repo-link"}, href=True)['href'],  
                    "stars": "-1",                 
                    "forks": "-1",
                    "watchers": repo_metadata_li[0].find('a').text.strip().replace(" watchers", "").replace(" watcher", ""),
                    "updated_on": repo_metadata_li[1].find('time')['datetime'],
                    "keywords": keyword_split,
                    "source": "Bitbucket",
                    "uuid" : str(uuid.uuid4()),                      
                }
                # Append repo
                data.append(datarepo)
            
            # Since we use web requests it is good to wait between requests to avoid IP bans
            time.sleep(random.uniform(0.1, 0.4))
            # Repos in one page end

        # Max pages end
        # Create dataframe from json list & export one csv per keyword
        df_bitbucket_web = pd.json_normalize(data=data)
        del data
        df_bitbucket_web.reset_index(drop=True, inplace=True)

        file_name = "Bitbucket_kw_"

        # Clean
        df_bitbucket_web_cleaned = self.preprocess.clean_dataframe(df_bitbucket_web)
        del df_bitbucket_web
        
        if df_bitbucket_web_cleaned.empty:
            PrintLog.log("No VALID repos found for the given keywords in BitBucket.")  
            return df_bitbucket_web_cleaned # empty dataframe

        # Export
        SCRUtils.export_csv(df_bitbucket_web_cleaned, "./output/", file_name + keyword_split, True, True)

        # Upload
        PrintLog.log("Upload to elastic called from BitBucket crawler: " + file_name + keyword_split)                  
        self.elastic_end.upload_pandas(df_bitbucket_web_cleaned)

        return df_bitbucket_web_cleaned
