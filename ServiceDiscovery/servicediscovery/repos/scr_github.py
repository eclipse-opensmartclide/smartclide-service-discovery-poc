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

import time
import random
import requests  # requests.exceptions.Timeout
import re
import uuid
import json
import dateutil.parser as parser
import dateutil.tz as tz

# pygithub
from github import Github
from github import RateLimitExceededException
from github import BadCredentialsException
from github import GithubException

# own
from utils import SCRUtils, PrintLog
from database.database_handler import Database
from repos.clean_data import ServiceCrawledDataPreProcess


class NoReposFound(Exception):
    pass


class CrawlerGitHub:

    preprocess = ServiceCrawledDataPreProcess()

    N_REPOS_EXPLORE = 50  # Number of repos to explore

    def __init__(self, ptoken):
        """
        Creates an isntance of CrawlerGitHub using the ptoken argument.
        """
        self.token = Github(ptoken)  # pygithub li

    def get_from_topic(self, p_topic):
        """
        Parses the topic given to search for repositories in GitHub
        """
        # Filter by topics? ex: api, service, rest, swagger
        # We look for the topics
        topics = [topic.strip() for topic in p_topic.split(',')]
        # Make sure we have valid keywords names
        # [^A-Za-z0-9+]+
        topics = [re.sub('[^A-Za-z0-9+]+', '', key) for key in topics]

        query = ''
        # for each topics, build the query
        for topic_item in topics:
            query = f'{query}topic:{topic_item} '  # space is important

        # get github repos using a topic
        try:
            repos = self.token.search_repositories(query, 'stars', 'desc')
            if repos.totalCount == 0:
                raise NoReposFound
            # Only explore the  the top repos
            repos_s = repos[:self.N_REPOS_EXPLORE]
            return self.get_repos(repos_s, p_topic, from_topic=True)

        except BadCredentialsException:
            PrintLog.log("\n[GitHub] Token is not valid")
        except NoReposFound:
            PrintLog.log("\n[GitHub] No data found for that topic")

    def get_from_url(self, url):
        """
        Parses the URL given to search for repositories in GitHub, username or organization.
        """
        # find all the text btw / and get the last [-1], the org/user
        # https://github.com/dabm-git/ --> [https:] [github.com] [dabm-git]
        username = re.findall("([^\/]+)", url)[-1]

        try:
            # target can be username or an organization
            user = self.token.get_user(username)
            user_repos = user.get_repos()
            # Note: repos that are forks are not listed in the user_repos
            if user_repos.totalCount == 0:
                raise NoReposFound
            return self.get_repos(user_repos, username, from_url=True)

        except BadCredentialsException:
            PrintLog.log("\n[GitHub] Token is not valid")
        except NoReposFound:
            PrintLog.log(f"\n[GitHub] No data found for the user: {user}")

    def get_from_keywords(self, keywords):
        """
        Parses the keywords given to search for repositories in GitHub.
        """
        # Split the search keywords in case of multiple keywords
        keywords = [keyword.strip() for keyword in keywords.split(',')]
        # Make sure we have valid keywords names
        keywords = [re.sub('[^A-Za-z0-9+]+', '', key) for key in keywords]
        keywords = '+'.join(keywords)

        # We look for the keywords at the readme, the project description and name
        query = f'{keywords}+in:name+in:readme+in:description'

        # Filter by +stars
        try:
            repos = self.token.search_repositories(query, 'stars', 'desc')
            if (repos.totalCount != 0):  # check if paginated list is empty
                # Only explore the top repos
                repos_s = repos[:self.N_REPOS_EXPLORE]
            else:
                raise NoReposFound

            return self.get_repos(repos_s, keywords, from_keywords=True)

        except BadCredentialsException:
            PrintLog.log("\n[GitHub] Bad credentials")
        except NoReposFound:
            PrintLog.log(
                f"\n[GitHub] No data found for the keywords: {keywords}")

    def get_repos(self, payload, keywords, from_url=False, from_keywords=False, from_topic=False):
        """
        Search for repositories in GitHub based on the payload given and the type of search,
        from URL or Keyword using get requests on its API.
        """
        # Note: results are paginated
        data = []

        PrintLog.log(f"[GitHub] Get GitHub repos started: {keywords}")

        # while True then raise StopIteration
        while True:
            try:
                for repo in payload:
                    # https://docs.github.com/es/rest/repos/repos#get-a-repository

                    # Make sure we have strings
                    clone_url = str(repo.clone_url)
                    description = str(repo.description)
                    language = str(repo.language)
                    updated_at = parser.parse(str(repo.updated_at)).replace(
                        tzinfo=tz.gettz('UTC')).isoformat()
                    created_at = parser.parse(str(repo.created_at)).replace(
                        tzinfo=tz.gettz('UTC')).isoformat()
                    deployable = 0

                    try:
                        # check if the repo has a deployable file
                        has_dockerfile = repo.get_contents("Dockerfile")
                        if has_dockerfile:
                            deployable = 1  # DB expects 1 or 0, not True or False
                    except GithubException:
                        deployable = 0

                    try:
                        # get the license name
                        license_name = str(repo.get_license().license.key)
                    except Exception as e:
                        license_name = ""

                    stars = str(repo.stargazers_count)
                    forks = str(repo.forks_count)
                    watchers = str(repo.watchers_count)
                    topics = ','.join(repo.get_topics())

                    # + spacer, "," is used in the .csv file
                    merged_kw = keywords.replace('+', ',')
                    # If we have more topics, merge them with the kw
                    if topics:
                        merged_kw = f"{keywords},{topics}"
                    merged_kw_list = merged_kw.split(',')

                    # Get the repo name from url
                    # Find the words after url / and remove .git
                    name = re.findall("([^/]*)$", clone_url)
                    full_name = name[0].replace('.git', '')

                    # Build the data
                    datarepo = {
                        "id": str(uuid.uuid4()),
                        "name": full_name,
                        "user_id": "ee123203cb634a4eb9edd7ec582d099f",
                        "registry_id": "aa123203sd424a45b9edd7ec582d093a",
                        "git_credentials_id": "628c922780b42501489a85dd",
                        "url": clone_url,
                        "description": description,
                        "is_public": True,
                        "licence": license_name,
                        "framework": language,
                        "created": created_at,
                        "updated": updated_at,
                        "stars": int(stars),
                        "forks": int(forks),
                        "watchers": int(watchers),
                        "deployable": deployable,
                        "keywords": merged_kw_list,
                    }
                    data.append(datarepo)

                    # Random delay to avoid requests timeout in GitHub API
                    time.sleep(random.uniform(0.1, 0.5))

                # loop result end
                raise StopIteration

            except BadCredentialsException:
                PrintLog.log("[GitHub] Token is not valid")
                break
            except StopIteration:
                if not data:
                    PrintLog.log(
                        "[GitLab] No valid repos found for the given input.")
                    return {}  # empty dict
                else:
                    file_name = "GitHub_"
                    if from_url:
                        file_name = "GitHub_url_"
                    if from_keywords:
                        file_name = "GitHub_kw_"
                    if from_topic:
                        file_name = "GitHub_topic_"

                    # Clean and export the data
                    data_cleaned = data if from_url else self.preprocess.clean_export_data(
                        data)

                    # at this point we have some data, so we can upload it to the database
                    PrintLog.log(
                        "[GitHub] Upload to database called from GitHub crawler")
                    insert_status = False
                    res = Database().insert_service(data_cleaned, file_name + keywords)
                    if res.status_code > 199 and res.status_code < 300:
                        insert_status = True
                        PrintLog.log("[GitHub] Upload to database successful")
                    else:
                        PrintLog.log(
                            f"[GitHub] Error while inserting data into database: {res}")
                    PrintLog.log(
                        f"[GitHub] Get repos finished, total services found: {len(data_cleaned)}")
                    return insert_status, len(data_cleaned)

            except requests.exceptions.Timeout:
                PrintLog.log("[GitHub] Requests Timeout")
                # Waint and relaunch the repo search ?
                time.sleep(15)

            except RateLimitExceededException:
                # Default wait time in GitHub Docs> 1 hour
                PrintLog.log(
                    "[GitHub] RateLimitExceededException, Sleeping (1h)")
                # TODO: change token?
                time.sleep(3600)

        # while loop end
        return {}  # empty dict if no data or exception
