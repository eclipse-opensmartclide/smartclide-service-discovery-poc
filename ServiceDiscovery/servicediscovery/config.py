#!/usr/bin/python3
# Eclipse Public License 2.0

class FlaskConfig():
	# API config
	PORT = 2020
	HOST = '0.0.0.0'
	URL_PREFIX = '/servicediscovery/v1'
	DEBUG_MODE = False
	USE_HTTPS = DEBUG_MODE
	SSL_KEY = './certs/server.key'
	SSL_CERT = './certs/server.crt'

# scr tokens
class ServiceDiscoeryConfig():
    # The tokens are examples and are not valid
	# GitHub API
	GITHUB_ACCESS_TOKEN_1 = 'redacted'
	# GitLab API
	GITLAB_ACCESS_TOKEN_1 = 'redacted'
	# BitBucket API
	BITBUCKET_ACCESS_TOKEN_1 = 'redacted'
 
	# More tokens....
	GITHUB_ACCESS_TOKEN_2 = 'redacted'
