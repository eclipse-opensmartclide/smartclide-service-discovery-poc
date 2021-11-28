#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import fields

from servicediscovery.api.v1 import api

github_model = api.model("GitHub model", {
    'from_url': fields.String(example='https://github.com/dabm-git', description='Url of a user or organization'),
    'from_keyword': fields.String(example='dabm', description='Keyword or list of keywords separated by coma to get data from.'),
    'from_topic': fields.String(example='api', description='Topic to get data from.')
}, description='Information of the Crawler GitHub in the API.')

