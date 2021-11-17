#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import fields

from scr.api.v1 import api

gitlab_model = api.model("GitLab model", {
    'from_url': fields.String(example='https://gitlab.com/dabm-git', description='Url of a user or organization'),
    'from_keyword': fields.String(example='dabm', description='keyword or list of keywords separated by coma to get data from.')
}, description='Information of the Crawler GitLab in the API.')

