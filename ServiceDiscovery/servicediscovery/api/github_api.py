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
from utils import FlaskUtils, PrintLog
from config import ServiceDiscoeryConfig

# github
from api.parsers.github_parser import github_argument_parser
from repos.scr_github import CrawlerGitHub

github_ns = api.namespace('crawl_github', description='Crawler GitHub')


@github_ns.route('', methods=['GET'])  # url/user
class GetGitHubRepos(Resource):
    @limiter.limit('1000/hour')
    @cache.cached(timeout=84600, query_string=True)
    @api.expect(github_argument_parser)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    def get(self):
        """
        Returns a JSON array with the repo information
        """
        # retrieve and chek arguments
        is_from_url = False
        is_from_keyword = False
        is_from_topic = False
        r_json = ""
        try:
            args = github_argument_parser.parse_args()
            from_url = args['from_url']
            from_keyword = args['from_keyword']
            from_topic = args['from_topic']
            # None
            if from_keyword is None and from_url is None and from_topic is None:
                raise ValueError("from_keyword or from_url is not provided")
            if from_url:
                if from_keyword and from_topic:
                    raise ValueError("from_keyword or from_url not both")
                else:
                    is_from_url = True
            if from_keyword:
                is_from_keyword = True
            if from_topic:
                is_from_topic = True

        except Exception as e:
            return FlaskUtils.handle400error(github_ns, 'The providen arguments are not correct.')

        try:
            github = CrawlerGitHub(ServiceDiscoeryConfig.GITHUB_ACCESS_TOKEN_1)
            if is_from_url:
                i, n = github.get_from_url(from_url)
            if is_from_keyword:
                i, n = github.get_from_keywords(from_keyword)
            if is_from_topic:
                i, n = github.get_from_topic(from_topic)
            inserted, n_repos = i or None, n or None
        except Exception as e:  # Config can raise an exception
            return FlaskUtils.handle503error(github_ns, 'GitHub service discovery is unavailable.')

        if not n_repos:
            return {"success": False, "message": "No GitHub repos found."}

        inserted_str = (
            "and uploaded successfully to the database"
            if inserted
            else "but not uploaded to the database, check the database connection."
        )
        return {"success": True, "message": f"{n_repos} GitHub repos found {inserted_str}"}
