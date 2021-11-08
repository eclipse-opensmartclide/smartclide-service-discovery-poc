#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import reqparse

github_argument_parser = reqparse.RequestParser()

github_argument_parser.add_argument('from_url',
							location='args',
							type=str,
							required=False,
							default=None,
							help='The GitHub URL user/org to retrieve repo information from.')

github_argument_parser.add_argument('from_keyword',
							location='args',
							type=str,
							required=False,
							default=None,
							help='The keyword to retrieve repo information from.')
github_argument_parser.add_argument('from_topic',
							location='args',
							type=str,
							required=False,
							default=None,
							help='The topic to retrieve repo information from.')