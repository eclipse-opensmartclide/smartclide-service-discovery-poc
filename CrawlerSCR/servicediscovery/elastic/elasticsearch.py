#!/usr/bin/python3
# Eclipse Public License 2.0

import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from configparser import ConfigParser
import json

from servicediscovery.utils import PrintLog

class Elastic():

    elastic = None

    def __init__(self):
        self.elastic = self.__configure_elastic()        
        
    def __configure_elastic(self):
        # connect to elasticserach        
        config = self.__config()
        PrintLog.log('[elastic] Connecting to Elasticsearch.')
    
        return Elasticsearch(
             [config['host']+ ':' + config['port']],
             http_auth=(config['user'], config['password']),
             scheme="http", # SSL?
             verify_certs=False,
             http_compress=True
         )

    def __config(self, filename='database.ini', section='elastic'):
        """
        Function for parsing the configuration file of the elasticsearch
        """  
        parser = ConfigParser()
        parser.read(filename)
        if not parser.has_section(section):
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        params = parser.items(section)
        return {param[0]: param[1] for param in params}
    
    def __del_duplicates():
        # remove duplicates from elasticsearch index
        # TODO      
        pass
    
    # Get rid of blank values
    def __safe_value(self, colum):
        return colum if not pd.isna(colum) else "Other"
    
    # Generate documents for bulk upload
    def __doc_generator(self, df):
         # row into a document
        df_iter = df.iterrows()       
        for index, document in df_iter:
            yield {
                    "_index": 'scr_index', # index of crawled data
                    #"_type": "_doc", # decrapated
                    "_id" : f"{document['full_name']}", # use the full name as id user+serviceName
                    "_source": document.to_dict(), # use a filter?
                }    
        
    def upload_pandas(self, pd_to_up):                
        # Upload to elastic the cleaned pandas using helpers bulk and doc_generator
        PrintLog.log('[elastic] Uploading pandas using bulk and doc_generator.')  
                 
        helpers.bulk(self.elastic, self.__doc_generator(pd_to_up))

    def search(self, json_data):                
        # Upload to elastic the cleaned pandas using helpers bulk and doc_generator
        PrintLog.log('[elastic] Searching in elastic.')

        # Normalize json
        json_query = json.loads(json_data)
        
        # To daraframe, this step is not necessary since we can acces the json directly
        query_dataframe = pd.DataFrame.from_dict(json_query)

        # TODO: Use DLE to classify the query to get the right keywords
        # Build query
        query = query_dataframe["full_name"][0] + " OR " +  query_dataframe["description"][0] # + " OR " + query_dataframe["keywords"][0]
        
        query_body ={
            "query": {
                "query_string" : {
                "fields" : ["description", "full_name"], #"keywords"],
                "query" : query,
                }
            }
        }        
        # The actual search in the scr index
        result = self.elastic.search(index="scr_index", body=query_body) # scr_index

        # Filter by hits
        all_hits = result['hits']['hits']
        # No hits?
        if all_hits == []:
            return {"0" :"No services have been found for that query. The Crawler subcomponent will search for it. Try again later."}

        # We have hits!
        # Iterate the nested dictionaries inside the ["hits"]["hits"] list
        hits = [json.dumps(doc) for num, doc in enumerate(all_hits)]
            
        return json.dumps(hits) # return the json
        
        
        
        
        
        