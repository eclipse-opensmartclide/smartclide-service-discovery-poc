#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import fields

from api.v1 import api

bitbucket_model = api.model("Bitbucket model", {
    'from_keyword': fields.String(example='dabm', description='keyword or list of keywords separated by coma to get data from.')
}, description='Information of the Crawler Bitbucket in the API.')

