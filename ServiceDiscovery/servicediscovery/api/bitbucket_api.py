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
                raise ValueError("from_keyword is none")

        except Exception as e:
            return FlaskUtils.handle400error(bitbucket_ns, f'The providen arguments are not correct. {e}')

        # retrieve repos
        try:
            bitbucket = CrawlerBitbucket()
            i, n = bitbucket.get_from_keywords_web(from_keyword)
            inserted, n_repos = i or None, n or None
        except Exception as e:  # CrawlerBitbucket exceptions
            return FlaskUtils.handle503error(bitbucket_ns, 'Bitbucket service discovery is unavailable')

        if not n_repos:
            return {"success": False, "message": "No Bitbucket repos found."}

        inserted_str = (
            "and uploaded successfully to the database"
            if inserted
            else "but not uploaded to the database, check the database connection."
        )
        return {"success": True, "message": f"{n_repos} Bitbucket repos found {inserted_str}"}
