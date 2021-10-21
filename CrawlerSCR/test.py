#!/usr/bin/python3
# Eclipse Public License 2.0

from scr.config import SCRConfig
from scr.utils import SCRUtils

from scr.repos.scr_github import CrawlerGitHub
from scr.repos.scr_gitlab import CrawlerGitLab
from scr.repos.scr_bitbucket import CrawlerBitbucket

# Remote call
import requests
import json
import pandas as pd    
import concurrent.futures

class RemoteKWGithub:
	def get_keywords(self, file):
		# Initial var
		with open(f"{file}") as f:			  
			keywords = [line.rstrip('\n').lower() for line in f]
		return keywords

	def call_api(self, kw):
		if not kw:
			return pd.DataFrame()
		get_params = {'from_keyword':kw}
		# Todo handle error codes
		response = requests.get("http://localhost:5000/scr/v1/github", params=get_params)
		a_json = json.loads(response.text)
		return pd.DataFrame.from_dict(a_json)

	def remote_github_kw_from_file(self, file_name):
		keywords = self.get_keywords(file_name)
		tasks = []
		data = pd.DataFrame()
		# Iterate keywords on threads
		with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
			for line in keywords:
				print("Task submited")
				tasks.append(executor.submit(self.call_api, line))

		    # Iterate results
			print("Union results")
			# Todo union the dataframe generated in the API call
			for result in concurrent.futures.as_completed(tasks):
				data = data.append(result.result(), ignore_index=True)
                
		SCRUtils.export_csv(data, "./", "merged", True, True)
		return data

if __name__ == '__main__':

	githubia = RemoteKWGithub()
	print(githubia.remote_github_kw_from_file("keywords_w.txt"))