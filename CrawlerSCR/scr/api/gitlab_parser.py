#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import reqparse

gitlab_argument_parser = reqparse.RequestParser()

gitlab_argument_parser.add_argument('from_url',
							location='args',
							type=str,
							required=False,
							default=None,
							help='The GitLab URL user/org to retrieve repo information from.')

gitlab_argument_parser.add_argument('from_keyword',
							location='args',
							type=str,
							required=False,
							default=None,
							help='The keyword to retrieve repos information from.')