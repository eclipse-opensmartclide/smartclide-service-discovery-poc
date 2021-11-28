#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import Api
from flask_restx import Resource
from flask import request
import pandas as pd
from io import StringIO
import json

from core import cache, limiter
from elastic.elasticsearch import Elastic

api = Api(version='1.0',
          title='Service Discovery API',
          description="** Service Discovery Flask RESTX API **")

insert_ns = api.namespace('service_insert', description='Insert a new service to the registry')
@insert_ns.route('', methods = ['POST']) # url/user
class GetStatus(Resource):
    @limiter.limit('1000/hour')
    @cache.cached(timeout=84600, query_string=True)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    @api.doc(params={ 'id': 'Specify the Id associated with the person' })
    def post(self):
        if request.method != 'POST':      
            return

        # get data from POST
        content = request.json

        # check if content is empty
        if content is None:
            return {'message': 'Empty POST content'}, 400

        # check if content is valid JSON
        try:
            json.loads(content)
        except TypeError:
            return 'Invalid parameter format, only JSON is acepted', 400


        # try to convert the data to a dataframe
        try:
            df = pd.json_normalize(json.loads(content))
        except:
            return "Invalid data format", 400

        # remove .0 from the colum names
        df.columns = [col.replace('.0', '') for col in df.columns]
        
        # check if df have the right columns and the content of any is not empty
        if not set(['full_name', 'link', 'stars', 'forks', 'watchers', 'updated_on', 'keywords', 'source', 'uuid']).issubset(df.columns):
            return "Invalid data format, the inserted columns are not correct to perform an insertion, check that all columns have data.", 400

        # TODO: check if the content of the colunms is not empty

        # convert df.source to lowercase
        df['source'] = df['source'].str.lower()
  
        # check the source of the dataframe
        if df.source.str.contains('github').any() or df.source.str.contains('bitbucket').any() or df.source.str.contains('gitlab').any():
            return 'Invalid data, source must not be github or bitbucket or gitlab', 400
    

        # insert data to elastic
        Elastic().upload_pandas(df)
        # export data to csv usin the file name full_name from the dataframe df

        df.to_csv('output/SmartCLIDE_insert_' + df['full_name'][0] + '.csv', index=False)
       
        return 'Data inserted', 200
