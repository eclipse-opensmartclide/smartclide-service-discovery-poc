#!flask/bin/python
# Eclipse Public License 2.0


from CrawlerSCR.servicediscovery import elastic
from flask_restx import Api
from flask_restx import Resource
from flask import request
import pandas as pd
from io import StringIO

from servicediscovery.core import cache, limiter
from servicediscovery.elastic.elasticsearch import Elastic

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
    def post(self):
        if request.method != 'POST':      
            return

        # get data from POST
        content = request.json
        
        # try to convert the data to a dataframe
        try:
            df = pd.read_csv(StringIO(content))
        except:
            return "Invalid data format", 400

        # check if df have the right columns and the content of any is not empty
        if not df.empty and df.columns.tolist() == ['full_name', 'description', 'link', 'stars', 'forks', 'watchers', 'updated_on', 'keywords', 'source', 'uuid']:
            for index, row in df.iterrows():
                if not row['full_name'] or not row['description'] or not row['link'] or not row['stars'] or not row['forks'] or not row['watchers'] or not row['updated_on'] or not row['keywords'] or not row['source'] or not row['uuid']:
                    return 'Invalid data, missing values in some columns', 400


        # convert df.source to lowercase
        df['source'] = df['source'].str.lower()
  
        
        # check the source of the dataframe
        if df.source.str.contains('github').any() or df.source.str.contains('bitbucket').any() or df.source.str.contains('gitlab').any():
            return 'Invalid data, source must not be github or bitbucket or gitlab', 400
    

        # insert data to elastic
        Elastic().upload_pandas(df)
        # export data to csv usin the file name full_name from the dataframe df
        df.to_csv(f'output/up_{df.full_name}.csv', index=False)
       
        return 'Data inserted', 200
