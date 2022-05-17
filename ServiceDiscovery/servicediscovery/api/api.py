#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import Api

api = Api(version='1.0',
          title='Service Discovery API',
          description="SmartCLIDE - Service Discovery Flask RESTX API")
