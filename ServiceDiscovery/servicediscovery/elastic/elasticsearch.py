#!/usr/bin/python3
# Eclipse Public License 2.0

import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json

from utils import PrintLog, ConfigReader

class Elastic():

    elastic = None
    index = 'scr_index'

    def __init__(self):
        self.elastic = self.__configure_elastic()        
        
    def __configure_elastic(self):
        # connect to elasticserach        
        config = ConfigReader.read_config(section='elastic')

        PrintLog.log('[elastic] Connecting to Elasticsearch.')

        self.index = config['index']
        return Elasticsearch(
             [config['host']+ ':' + config['port']],
             http_auth=(config['user'], config['password']),
             scheme=config['scheme'], # SSL?
             verify_certs=False,
             http_compress=True
         )
        
    # Get rid of blank values
    def __safe_value(self, colum):
        return colum if not pd.isna(colum) else "Other"
    
    # Generate documents for bulk upload
    def __doc_generator(self, df):
         # row into a document
        df_iter = df.iterrows()       
        for index, document in df_iter:
            yield {
                    "_index": self.index, # index of crawled data
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
        PrintLog.log('[elastic] Searching in Elasticsearch.')

        # Normalize json        
        json_query = json.loads(json_data)
        
        # To daraframe, this step is not necessary since we can acces the json directly..
        query_dataframe = pd.DataFrame.from_dict(json_query)

        # TODO: Check if we have the colums we need, full_name and description
        # TODO: Use DLE to classify the query to get the right keywords based on the description

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

        # TODO: Self call the crawler to get the data if all_hits is empty

        # We have hits!
        # Iterate the nested dictionaries inside the ["hits"]["hits"] list
        hits = [json.dumps(doc) for num, doc in enumerate(all_hits)]

        # TODO, normalize socres of the hits            
        return json.dumps(hits) # return the json with the hits
        
        
        
        
        
        