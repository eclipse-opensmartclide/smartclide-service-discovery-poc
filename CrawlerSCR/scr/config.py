#!/usr/bin/python3
# Eclipse Public License 2.0

class FlaskConfig():
	# api config
	PORT = 5000
	HOST = '0.0.0.0'
	URL_PREFIX = '/scr/v1'
	DEBUG_MODE = True
	USE_HTTPS = not DEBUG_MODE
	SSL_KEY = './certs/server.key'
	SSL_CERT = './certs/server.crt'

# scr tokens
class SCRConfig():
	# GitHub API
	GITHUB_ACCESS_TOKEN_1 = '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'
	# GitLab API
	GITLAB_ACCESS_TOKEN_1 = 'KTsSwjwCQ7tN4pYCMsyb'
	# BitBucket API
	BITBUCKET_ACCESS_TOKEN_1 = 'todo'
 
 
	# More tokens..
	GITHUB_ACCESS_TOKEN_2 = 'todo'

