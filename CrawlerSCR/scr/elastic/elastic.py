#!/usr/bin/python3
# Eclipse Public License 2.0

from configparser import ConfigParser

from scr.utils import PrintLog
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
from configparser import ConfigParser

from scr.repos.clean_data import ServiceCrawledDataPreProcess

class elastic():
    
    preprocess = ServiceCrawledDataPreProcess() # ZK work

    def configure_elastic(self):
        # connect to elasticserach        
        config = self.config()
        PrintLog.log('[elastic] Connecting to the Elasticsearch database...')
    
        es = Elasticsearch(
            [config['host']+ ':9200'], # default port
            #http_auth=('user', 'secret'),
            scheme="http",
            verify_certs=False,
            http_compress=True
        )
        return es
    
    def config(self, filename='database.ini', section='elastic'):
        """
        Function for parsing the configuration file of the elasticsearch
        """  
        parser = ConfigParser()    
        parser.read(filename)
        # get section, default to elastic
        cfg_file = {}
        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                cfg_file[param[0]] = param[1]
        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return cfg_file
    
    def del_duplicates():
        # remove duplicates from elasticsearch index
        # TODO      
        pass
    
    # Get rid of blank values
    def safe_value(self, colum):
        return colum if not pd.isna(colum) else "Other"
    
    # Generate documents for bulk upload
    def doc_generator(self, df):
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
        
        # Connect to elasticsearch
        elastic = self.configure_elastic()
        
        # Upload to elastic the cleaned pandas using helpers bulk and doc_generator
        PrintLog.log('[elastic] Uploading pandas using bulk and doc_generator.')           
        helpers.bulk(elastic, self.doc_generator(pd_to_up))
         
        
        
        
        
        
        
        