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
from api.api import api
from core import cache, limiter
from utils import FlaskUtils
from config import ServiceDiscoeryConfig

# gitlab
from api.parsers.gitlab_parser import gitlab_argument_parser
from repos.scr_gitlab import CrawlerGitLab

gitlab_ns = api.namespace('crawl_gitlab', description='Crawler GitLab')


@gitlab_ns.route('', methods=['GET'])  # url/user
class GetGitLabRepos(Resource):
    @limiter.limit('1000/hour')
    @cache.cached(timeout=84600, query_string=True)
    @api.expect(gitlab_argument_parser)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    def get(self):
        """
        Returns a str with the search info
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
                raise ValueError("from_keyword or from_url is not provided")
            # Both
            if from_url and from_keyword:
                raise ValueError("from_keyword or from_url not both")
            # Only one
            if from_url:
                is_from_url = True
            else:
                is_from_keyword = True

        except Exception as e:
            #raise e
            return FlaskUtils.handle400error(gitlab_ns, f'The providen arguments are not correct. Please, check the swagger documentation at /v1 {e}')

        # retrieve repos
        try:
            gitlab = CrawlerGitLab(ServiceDiscoeryConfig.GITLAB_ACCESS_TOKEN_1)
            if is_from_url:
                i, n = gitlab.get_from_url(from_url)
            if is_from_keyword:
                i, n = gitlab.get_from_keywords(from_keyword)
            inserted, n_repos = i or None, n or None
        except Exception as e:  # CrawlerGitLab exceptions
            return FlaskUtils.handle503error(gitlab_ns, 'GitLab service discovery is unavailable.')

        if not n_repos:
            return {"success": False, "message": "No GitLab repos found."}

        inserted_str = (
            "and uploaded successfully to the database"
            if inserted
            else "but not uploaded to the database, check the database connection."
        )
        return {"success": True, "message": f"{n_repos} GitLab repos found {inserted_str}"}
