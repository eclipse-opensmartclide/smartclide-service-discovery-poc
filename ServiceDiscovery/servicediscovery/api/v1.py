#!flask/bin/python
# Eclipse Public License 2.0

from flask_restx import Api
from flask_restx import Resource
from flask import request
import pandas as pd
import json

from core import cache, limiter
from elastic.elasticsearch import Elastic

from utils import PrintLog, FlaskUtils

api = Api(version='1.0',
          title='Service Discovery API',
          description="** Service Discovery Flask RESTX API **")

insert_ns = api.namespace('service_insert', description='Insert a new service to the Elasticsearch registry')
@insert_ns.route('', methods = ['POST']) # url/user
class GetStatus(Resource):
    @limiter.limit('1000/hour')
    @cache.cached(timeout=1, query_string=True)
    @api.response(404, 'Data not found')
    @api.response(500, 'Unhandled errors')
    @api.response(400, 'Invalid parameters')
    @api.response(503, 'Service Unavailable')
    def post(self):
        if request.method != 'POST':      
            return

        # get data from POST
        try:
            if not (content := request.get_json()):
                FlaskUtils.handle400error(insert_ns, "Empty POST data")                
        except Exception:
            FlaskUtils.handle400error(insert_ns, "Invalid data format")            

        # try to convert the data to a dataframe
        try:
            # if is dict, convert to string
            if (type(content) == dict):
                content = json.dumps(content)
            df = pd.json_normalize(json.loads(content))
        except Exception:
            FlaskUtils.handle400error(insert_ns, "Invalid data format")


        # remove .0 from the colum names
        df.columns = [col.replace('.0', '') for col in df.columns]

        # check if df have all the right columns
        if not {
            'full_name',
            'link',
            'stars',
            'forks',
            'watchers',
            'updated_on',
            'keywords',
            'source',
            'uuid',
        }.issubset(df.columns):
            FlaskUtils.handle400error(insert_ns, "Invalid data format, the inserted columns are not correct to perform an insertion, check that all columns.")

        # convert df.source content to lowercase str
        df['source'] = df['source'].str.lower()

        # as it is a new insertion, it cannot be an source that we are using in the discovery process
        if df.source.str.contains('github').any() or df.source.str.contains('bitbucket').any() or df.source.str.contains('gitlab').any():
            FlaskUtils.handle400error(insert_ns, "Invalid data source, source must not be GitHub or Bitbucket or GitLab.")   

        PrintLog.log("[service_insert] Inserting new service to the Elasticsearch registry: \n" + str(df))

        try:               
            insrt_erros = Elastic().upload_pandas(df)
            if insrt_erros:
                FlaskUtils.handle503error(insert_ns,'Insert service is unavailable')

        except Exception as e:
            PrintLog.log("[service_insert] Insert service is unavailable, check Elasticseartch status")

            FlaskUtils.handle503error(insert_ns, 'Insert service is unavailable')
        # Export data to csv usin the file name full_name from the dataframe df
        df.to_csv('output/SmartCLIDE_insert_' + df['full_name'][0] + '.csv', index=False)

        return "{'status': 'Data inserted correctly', 'statusCode': '200'}"
        
