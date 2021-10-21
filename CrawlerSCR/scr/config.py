#!/usr/bin/python3
# Eclipse Public License 2.0

class FlaskConfig():
	# api config
	PORT = 2020
	HOST = '0.0.0.0'
	URL_PREFIX = '/scr/v1'
	DEBUG_MODE = True
	USE_HTTPS = not DEBUG_MODE
	SSL_KEY = './certs/server.key'
	SSL_CERT = './certs/server.crt'

# scr tokens
class SCRConfig():
    # The tokens are examples and are not valid
	# GitHub API
	GITHUB_ACCESS_TOKEN_1 = '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'
	# GitLab API
	GITLAB_ACCESS_TOKEN_1 = 'XPW9U4ZhzVSCRVW_2UxM'
	# BitBucket API
	BITBUCKET_ACCESS_TOKEN_1 = 'todo'
 
	# More tokens..
	GITHUB_ACCESS_TOKEN_2 = 'todo'

