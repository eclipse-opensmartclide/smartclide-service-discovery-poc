#!flask/bin/python
# Eclipse Public License 2.0

import json

from flask_restx import Resource

# scr API
from scr.api.v1 import api
from scr.core import cache, limiter
from scr.utils import FlaskUtils

# bitbucket
from scr.config import SCRConfig
#from scr.apibitbucket_model import bitbucket_model
from scr.api.bitbucket_parser import bitbucket_argument_parser
from scr.repos.scr_bitbucket import CrawlerBitbucket

bitbucket_ns = api.namespace('crawl_bitbucket', description='Crawler Bitbucket')

@bitbucket_ns.route('', methods = ['GET']) # url/user
class GetBitbucketRepos(Resource):
    @limiter.limit('1000/hour') 
    @cache.cached(timeout=84600, query_string=True)
    @api.expect(bitbucket_argument_parser)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    #@api.marshal_with(bitbucket_model, code=200, description='OK', as_list=True)
    def get(self):
        """
        Returns a JSON array with the repo information
        """
        # retrieve and chek arguments
        is_from_url = False
        is_from_keyword = False
        r_json = ""
        try:
            args = bitbucket_argument_parser.parse_args()
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
            return FlaskUtils.handle400error(bitbucket_ns, 'The providen arguments are not correct. Please, check the swagger documentation at /v1')

        # retrieve repos
        try:
            bitbucket = CrawlerBitbucket(SCRConfig.BITBUCKET_ACCESS_TOKEN_1)
            # TODO: param forks
            if is_from_url:                
                #r = bitbucket.get_from_url(from_url, get_forks=False)
                return FlaskUtils.handle500error(bitbucket_ns)
            if is_from_keyword:                
                r = bitbucket.get_from_keywords_web(from_keyword)
                
            if r.empty:
                r_json = ""
            else:                
                # split records index values table columns (the default format)
                result = r.to_json()    #orient="table")
                r_json = json.loads(result)

        except Exception as e:
            return FlaskUtils.handle500error(bitbucket_ns)

        # if there is not repos found  r_json == "", return 404 error
        if not r_json:
            return FlaskUtils.handle404error(bitbucket_ns, 'No Bitbucket repos was found for the given parameters.')
        
        # TODO: Shdl we return the raw repos found or the info about them? EX: found 39 new repos, inserted into the database ok.
        return r_json