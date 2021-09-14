#!flask/bin/python
# Eclipse Public License 2.0

import json

from flask_restx import Resource

from scr.api.v1 import api
from scr.core import cache, limiter
from scr.utils import FlaskUtils


# gitlab
from scr.config import SCRConfig
#from scr.api.gitlab_model import github_model
from scr.api.gitlab_parser import gitlab_argument_parser
from scr.repos.scr_gitlab import CrawlerGitLab

gitlab_ns = api.namespace('crawl_gitlab', description='Crawler GitLab')

@gitlab_ns.route('', methods = ['GET']) # url/user
class GetGitLabRepos(Resource):
    @limiter.limit('1000/hour') 
    @cache.cached(timeout=84600, query_string=True)
    @api.expect(gitlab_argument_parser)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    #@api.marshal_with(github_model, code=200, description='OK', as_list=True)
    def get(self):
        """
        Returns a JSON array with the repo information
        """
        # retrieve and chek arguments

        is_from_url = False
        is_from_keyword = False
        r_json = ""        
        try:
            args = gitlab_argument_parser.parse_args()
            from_url = args['from_url']
            from_keyword = args['from_keyword']
            # None
            if from_keyword is None and from_url is None:
                raise Exception("ValueError")
            # Both
            if from_url and from_keyword:
                raise Exception("ValueError")
            # Only one
            if from_url:
                is_from_url = True
            else:
                is_from_keyword = True

        except Exception as e:
            #raise e
            return FlaskUtils.handle400error(gitlab_ns, 'The providen arguments are not correct. Please, check the swagger documentation at /v1')

        # retrieve repos
        try:
            gitlab = CrawlerGitLab(SCRConfig.GITLAB_ACCESS_TOKEN_1)
            
            if is_from_url:                
                r = gitlab.get_from_url(from_url)
            if is_from_keyword:                
                r = gitlab.get_from_keywords(from_keyword)
            
            if r.empty:
                r_json = ""
            else:                
                # split records index values table columns (the default format)
                result = r.to_json()    #orient="table")
                r_json = json.loads(result)

        except Exception as e:
            return FlaskUtils.handle500error(gitlab_ns)

        # if there is not repos found  r_json == "", return 404 error
        if not r_json:
            return FlaskUtils.handle404error(gitlab_ns, 'No GitLab repos was found for the given parameters.')
        
        # TODO: Shdl we return the raw repos found or the info about them? EX: found 39 new repos, inserted into the database ok.
        
        return r_json