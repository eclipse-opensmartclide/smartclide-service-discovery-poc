#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import reqparse

bitbucket_argument_parser = reqparse.RequestParser()

bitbucket_argument_parser.add_argument('from_keyword',
                                       location='args',
                                       type=str,
                                       required=False,
                                       default=None,
                                       help='The keyword to retrieve repo information from.')
