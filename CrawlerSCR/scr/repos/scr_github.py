#!/usr/bin/python3
# Eclipse Public License 2.0

import time
import pandas as pd
import random
import requests # requests.exceptions.Timeout
import re

# pygithub
from github import Github
from github import RateLimitExceededException

# own
from scr.utils import SCRUtils, PrintLog
from scr.postgresql.config import postgresql

class CrawlerGitHub:
    # constructor
    def __init__(self, ptoken):
        """
        Creates an isntance of CrawlerGitHub using the ptoken argument.
        """
        self.token = Github(ptoken) # pygithub

    def get_from_url(self, url, get_forks):
        """
        Parses the URL given to search for repositories in GitHub.
        """
        # find all the text bwt / and get the last [-1] 
        # https://github.com/dabm-git/ --> [https:] [github.com] [dabm-git]
        username = re.findall("([^\/]+)", url)[-1]

        # target can be user/org
        user = self.token.get_user(username)
        user_repos = user.get_repos()

        # Dont get forks
        if not get_forks:
            non_forks = [trepo for trepo in user_repos if trepo.fork is False]
            repos = non_forks
        else:
            repos = user_repos
            # update the username for export  
            username = username + "_+forks"

        return self.get_repos(repos, username, from_url=True)
       
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

        # We look for the keywords at the readme and the project description
        query =  keywords + '+in:readme+in:description'

        # Filter by +stars
        repos = self.token.search_repositories(query, 'stars', 'desc')

        return self.get_repos(repos, keywords, from_keywords=True)

    def get_repos(self, payload, keywords, from_url = False, from_keywords = False):
        """
        Search for repositories in GitHub based on the payload given and the type of search,
        from URL or Keyword using get requests on its API.
        The result is exported to .csv files and then loaded into a Postgre database. 
        """ 

        # Limited to 1k for search, need more? paginate the results :P
        #PrintLog.log(f'Found {result.totalCount} repo(s) with the keywords',
        #      ','.join(keywords))
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

                    # Get the commits in reverse, so [0] is the last commit
                    # Since PaginatedList does not admit [-1]
                    commits = repo.get_commits().reversed                    
                    updated_on = str(commits[0].commit.author.date)
              
                    # If we have more topics, merge them with the kw
                    merged_kw = keywords                    
                    if topics:
                        merged_kw = keywords + "+" + topics

                    # Get the repo name from url
                    # Find the word after url / and remove .git
                    name = re.findall("([^/]*)$", str(clone_url))
                    full_name = name[0].replace('.git', '')

                    df_temp = pd.DataFrame({                        
                        'full_name': full_name,
                        'description': description,
                        'link': clone_url,
                        'stars': stars,
                        'forks': forks,
                        'watchers': watchers,
                        'updated_on': updated_on,
                        'keywords': merged_kw,
                        'source': "GitHub"
                        }, index=[0])

                    df_github = df_github.append(df_temp)
                    
                    # Random delay to avoid requests timeout
                    time.sleep(random.uniform(0.1, 0.3))

                # loop result end 
                raise StopIteration

            except StopIteration:
                # Backup, one file per keyword
                df_github.reset_index(drop=True, inplace=True)
                file_name = "GitHub_"
                if from_url:
                    file_name = "GitHub_url_"
                if from_keywords:
                    file_name = "GitHub_kw_"

                SCRUtils.export_csv(df_github, "./output/", file_name + keywords, True, True)               
                PrintLog.log("Inserting into github postgre db: " + file_name + keywords)      
                post = postgresql()
                post.upload_to_db("github", df_github)        
                #SCRUtils.upload_to_db("github", df_github)
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
                time.sleep(3600)
                pass

        # while loop end
        return df_github




       