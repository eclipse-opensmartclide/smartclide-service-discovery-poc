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

from flask_restx import Resource

# scr API
from api.api import api
from core import cache, limiter
from utils import FlaskUtils
from config import ServiceDiscoeryConfig

# bitbucket
from api.parsers.bitbucket_parser import bitbucket_argument_parser
from repos.scr_bitbucket import CrawlerBitbucket

bitbucket_ns = api.namespace(
    'crawl_bitbucket', description='Crawler Bitbucket')


@bitbucket_ns.route('', methods=['GET'])  # url/user
class GetBitbucketRepos(Resource):
    @limiter.limit('1000/hour')
    @cache.cached(timeout=84600, query_string=True)
    @api.expect(bitbucket_argument_parser)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    def get(self):
        """
        Returns a JSON array with the repo information
        """
        # retrieve and chek arguments
        r_json = None
        try:
            args = bitbucket_argument_parser.parse_args()

            from_keyword = args['from_keyword']

            # Only one
            if from_keyword is None:
                raise Exception("ValueError")

        except Exception as e:
            #raise e
            return FlaskUtils.handle400error(bitbucket_ns, 'The providen arguments are not correct.')

        # retrieve repos
        try:
            bitbucket = CrawlerBitbucket()
            r = bitbucket.get_from_keywords_web(from_keyword)
            r_json = r or ""

        except Exception as e:
            return FlaskUtils.handle503error(bitbucket_ns, 'Bitbucket service discovery is unavailable')

        # if there is not repos found  r_json == "", return 404 error
        if not r_json:
            return FlaskUtils.handle404error(bitbucket_ns, 'No Bitbucket repos was found for the given parameters.')

        # TODO: Shdl we return the raw repos found or the info about them? EX: found 39 new repositories
        return r_json
