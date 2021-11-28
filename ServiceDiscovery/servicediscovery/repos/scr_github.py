#!/usr/bin/python3
# Eclipse Public License 2.0

import time
import pandas as pd
import random
import requests # requests.exceptions.Timeout
import re
import uuid

# pygithub
from github import Github
from github import RateLimitExceededException
from github import BadCredentialsException
from github import GithubException

# own
from utils import SCRUtils, PrintLog
from servicediscovery.elastic.elasticsearch import Elastic
from servicediscovery.repos.clean_data import ServiceCrawledDataPreProcess

class NoReposFound(Exception):
    pass

class CrawlerGitHub:

    preprocess = ServiceCrawledDataPreProcess()
    elastic_end = Elastic()

    # constructor
    def __init__(self, ptoken):
        """
        Creates an isntance of CrawlerGitHub using the ptoken argument.
        """
        self.token = Github(ptoken) # pygithub
        
    def get_from_topic(self, p_topic):
        """
        Parses the topic given to search for repositories in GitHub
        """        
        # Filter by topics? ex: api, service, rest, swagger
        # We look for the topics
        query = 'topic:' + p_topic
        
        # get github repos using a topic
        try:
            repos = self.token.search_repositories(query, 'stars', 'desc')
            if (repos.totalCount != 0):
                pass # dont limit the search here
            else:
                raise NoReposFound
           
            return self.get_repos(repos, p_topic, from_topic=True)
        except BadCredentialsException: # GitHub Exc
            PrintLog.log("\nGitHub Bad credentials")
        except NoReposFound:
            PrintLog.log("\nNo data found for that topic")

    def get_from_url(self, url):
        """
        Parses the URL given to search for repositories in GitHub.
        """
        # find all the text bwt / and get the last [-1] the org/user
        # https://github.com/dabm-git/ --> [https:] [github.com] [dabm-git]
        username = re.findall("([^\/]+)", url)[-1]

        try: 
            # target can be user or an org
            user = self.token.get_user(username)
            user_repos = user.get_repos()
            # Note that repos forks are not listed in the user_repos! 
            # 
            if (user_repos.totalCount != 0):
                pass # dont limit the search here
            else:
                raise NoReposFound

            return self.get_repos(user_repos, username, from_url=True)
            
        except BadCredentialsException:
            PrintLog.log("\nGitHub Bad credentials")
        except NoReposFound:
            PrintLog.log("\nNo data found for that user")
            
    def get_from_keywords(self, keywords):
        """
        Parses the keywords given to search for repositories in GitHub.
        """
        # Split the search keywords in case of multiple
        keywords = [keyword.strip() for keyword in keywords.split(',')]
        # Make sure we have valid keywords names
        # [^A-Za-z0-9+]+
        keywords = [re.sub('[^A-Za-z0-9+]+', '', key) for key in keywords]
        keywords = '+'.join(keywords)

        # We look for the keywords at the readme, the project description and name
        query =  keywords + '+in:name+in:readme+in:description' # filter by api?

        # Filter by +stars
        try:   
            # Slice top 500 repos         
            repos = self.token.search_repositories(query, 'stars', 'desc')
            # check if paginated list is empty
            if (repos.totalCount != 0):
                repos_s = repos[:500] # In case of query is topic dont 
            else:
                raise NoReposFound
           
            return self.get_repos(repos_s, keywords, from_keywords=True)       
         
        except BadCredentialsException: # GitHub Exc
            PrintLog.log("\nGitHub Bad credentials")            
            
        except NoReposFound:
            PrintLog.log("\nNo data found for that query")            
            

    def get_repos(self, payload, keywords, from_url = False, from_keywords = False, from_topic = False):
        """
        Search for repositories in GitHub based on the payload given and the type of search,
        from URL or Keyword using get requests on its API.
        The result is exported to .csv files and then loaded into a Postgre database. 
        """ 
        # Note results are paginated
        df_github = pd.DataFrame()   
        
        df_github['full_name'] = ""
        df_github['link'] = ""
        df_github['description'] = ""
        df_github['stars'] = ""
        df_github['forks'] = ""
        df_github['watchers'] = ""
        df_github['updated_on'] = ""   
        df_github['keywords'] = ""
        df_github['source'] = ""
        df_github['uuid'] = ""

        PrintLog.log("Get GitHub repos started: " + keywords)
        # while True raise StopIteration
        while True:      
            try:
                for repo in payload:

                    # Make sure we have strings
                    clone_url = str(repo.clone_url)
                    description = str(repo.description)
                    stars = str(repo.stargazers_count)
                    forks = str(repo.forks_count)
                    watchers = str(repo.watchers_count)
                    
                    # + spacer due , is used in the .csv
                    topics = '+'.join(repo.get_topics())

                    try:
                        # Get the commits in reverse, so [0] is the last commit
                        # Since PaginatedList does not admit [-1]
                        commits = repo.get_commits().reversed                    
                        updated_on = str(commits[0].commit.author.date)
                    except GithubException as e:                        
                        continue # next repo, this one is empty

                    # If we have more topics, merge them with the kw
                    merged_kw = keywords                    
                    if topics:
                        merged_kw = keywords + "+" + topics

                    # Get the repo name from url
                    # Find the word after url / and remove .git
                    name = re.findall("([^/]*)$", str(clone_url))
                    full_name = name[0].replace('.git', '')
                    
                    # Build the dataframe TODO: change to dict so bitbucket and github are the same  df_temp = {  }
                    df_temp = pd.DataFrame({                        
                        'full_name': full_name,
                        'description': description,
                        'link': clone_url,
                        'stars': stars,
                        'forks': forks,
                        'watchers': watchers,
                        'updated_on': updated_on,
                        'keywords': merged_kw,
                        'source': "GitHub",
                        'uuid': str(uuid.uuid4())
                        }, index=[0])

                    df_github = df_github.append(df_temp)
                    
                    # Random delay to avoid requests timeout
                    time.sleep(random.uniform(0.1, 0.3))

                # loop result end
                raise StopIteration
            
            except BadCredentialsException:
                PrintLog.log("\nGitHub Bad credentials")
                break
            except StopIteration:
                # Backup, one file per keyword
                df_github.reset_index(drop=True, inplace=True)
                file_name = "GitHub_"
                if from_url:
                    file_name = "GitHub_url_"
                if from_keywords:
                    file_name = "GitHub_kw_"
                if from_topic:
                    file_name = "GitHub_topic_"
                
                # if df_github is empty, no data found
                if df_github.empty:
                    PrintLog.log("No VALID repos found for the given keywords in GitHub.")
                    break
                else:
                    # Clean
                    if not from_url:               
                        df_github_cleaned = self.preprocess.clean_dataframe(df_github)
                    else:
                        df_github_cleaned = df_github
                       
                    # Export
                    SCRUtils.export_csv(df_github_cleaned, "./output/", file_name + keywords, True, True) 
                    # Upload           
                    PrintLog.log("Upload pandas called from Github crawler: " + file_name + keywords)                  
                    self.elastic_end.upload_pandas(df_github_cleaned)
                        
                    break

            except requests.exceptions.Timeout:
                PrintLog.log("\nRequests Timeout")
                # Waint and relaunch the repo search ?
                time.sleep(15)
                pass

            except RateLimitExceededException:
                # Tiempo de espera segUn la doc es de 1h
                PrintLog.log("\nRateLimitExceededException")
                PrintLog.log("Sleeping (1h)") 
                # TODO: grab the wait time from API + change token?
                time.sleep(3600) # Default docs 1h
                pass

        # while loop end
        return df_github




       