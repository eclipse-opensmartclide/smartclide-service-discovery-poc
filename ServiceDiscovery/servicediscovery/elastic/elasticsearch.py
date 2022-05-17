#!/usr/bin/python3
# Eclipse Public License 2.0

import pandas as pd
import requests
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import json

from utils import PrintLog, ConfigReader
    
class Elastic():

    elastic = None
    index = 'scr_index'
    dle = 'localhost'
    
    def __init__(self):
        self.elastic = self.__configure_elastic()        
        
    def __configure_elastic(self):       
        dle_config = ConfigReader.read_config(section='dle')
        self.dle = dle_config['scheme'] + '://' + dle_config['host'] + ':' + dle_config['port'] + dle_config['endpoint']

        config = ConfigReader.read_config(section='elastic')
        self.index = config['index']
        
        try:
            ES_ENDPOINT = config['scheme'] + '://' + config['user'] + ':' + config['password'] + '@' + config['host'] + ':' + config['port']                                  
            return Elasticsearch([ES_ENDPOINT], api_key=(config['api_id'], config['api_key']))
        except Exception as error:
            PrintLog.log(f'[Elastic] Error: {str(error)}')
            return None
  
    # Get rid of blank values
    def __safe_value(self, colum):
        return "Other" if pd.isna(colum) else colum
    
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
        # TODO: If the connection is bad, retunr an error           
        # Upload to elastic the cleaned pandas using helpers bulk and doc_generator
        PrintLog.log('[Elastic] Uploading pandas using bulk and doc_generator called.')  
                 
        return helpers.bulk(self.elastic, self.__doc_generator(pd_to_up))        

    def search(self, json_data):                
        # Upload to elastic the cleaned pandas using helpers bulk and doc_generator
        PrintLog.log('[Elastic] Building the query.')

        # if the data is a dict, convert it to string then to json
        if (type(json_data) == dict):
            json_query = json.loads(json.dumps(json_data))
        else: # data is a string, convert it to json            
            json_query = json.loads(json_data)

        # To daraframe, this step is not necessary since we can acces the json directly...        
        query_dataframe = pd.DataFrame(json_query, index=[0])

        # Check if we have the colums we need, full_name and description
        if (
            'full_name' not in query_dataframe.columns
            or 'description' not in query_dataframe.columns
            or 'keywords' not in query_dataframe.columns
        ):                 
            return {"status" :"Columns full_name, description and keywords are required.", "statusCode" : 400}

        # check if full_name and description are not empty
        if (
            query_dataframe['full_name'][0] == ''
            or query_dataframe['description'][0] == ''         
        ):
            return {"status": "full_name and description data is required." , "statusCode" : 400}

        # if keywords is empty, call the dle endpoint
        if query_dataframe['keywords'][0] == '':
            PrintLog.log('[Elastic] Query keyword is empty, calling DLE service classification.')
            # TODO: debug this 
            class_params = {	
                "service_id": "1337",
                "method": "Default",
                "service_name": query_dataframe['full_name'][0],
                "service_desc": query_dataframe['description'][0]               
            }          
            response = requests.post(self.dle, json=json.dumps(class_params))
            if response.ok:
                query_dataframe['keywords'] = response.json()['service_class']            

        # Build query with the first row
        query = query_dataframe["full_name"][0] + " OR " +  query_dataframe["description"][0]

        if query_dataframe["keywords"][0] != "":
            query = query + " OR " + query_dataframe["keywords"][0]

        query_body ={
            "query": {
                "query_string" : {
                "fields" : ["description", "full_name", "keywords"],
                "query" : query,
                }
            }
        }

        PrintLog.log(f'[Elastic] Querying Elasticsearch: {query_body}')
        # The actual search in the scr index
        try:
            result = self.elastic.search(index=self.index, body=query_body)
        except Exception as e:
            PrintLog.log('[Elastic] Serach service is unavailable, check the Elasticsearch status')
            PrintLog.log(e)
            return {"status" : "Serach service is unavailable", "statusCode" : 503}

        # Filter by hits
        all_hits = result['hits']['hits']
        # No hits?
        if all_hits == []:
            if query_dataframe['keywords'][0] != '':                
                # slef call the github api
                kw = query_dataframe['keywords'][0]
                get_params = {'from_keyword': kw}
                # TODO: parametrize the url and handle request errors
                _ = requests.get("http://localhost:2020/scr/v1/crawl_github", params=get_params)

            return {"status" :"No services have been found for that query. The Crawler subcomponent will search for it. Try again later.", "statusCode" : 200}

        #  We have hits! Iterate the nested dictionaries inside the ["hits"]["hits"] list       
        hits = [json.dumps(doc) for _, doc in enumerate(all_hits)]

        return json.dumps(hits) # return the json with the hits
        
        
        
        
        
        
        