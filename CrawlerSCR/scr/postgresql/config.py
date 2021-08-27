#!/usr/bin/python
# Eclipse Public License 2.0

import psycopg2
from sqlalchemy import create_engine
from configparser import ConfigParser

from scr.utils import PrintLog

# TODO: refactor postgresql and config.py

class postgresql():
    
    def upload_to_db(self, table, dataframe):
        """
        Main call cascade function to:
        create database tables, if there are none, 
        insert a dataframe into a table
        and handle duplicates for that table.
        """    
        # Create tables if not exists
        self.init_create_tables()
        # Insert the data, no primary keys  
        self.insert_dataframe_into_table(table, dataframe)
        # Handle dupes in the modified table
        self.delete_duplicates(table)
        
    def config(self, filename='database.ini', section='postgresql'):
        """
        Function for parsing the configuration file of the postgre db.
        """  
        parser = ConfigParser()
        parser.read(filename)
        if not parser.has_section(section):
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        params = parser.items(section)
        return {param[0]: param[1] for param in params}
    
    def test_connection(self):
        """
        Function for testning the postgre db connection printing the db version.
        """  
        conn = None
        try:
            params = self.config()                      
            PrintLog.print_log('Connecting to the PostgreSQL database...')
            conn = psycopg2.connect(**params)           
            cur = conn.cursor()            
            # execute a statement
            PrintLog.print_log('PostgreSQL database version:')
            cur.execute('SELECT version()')
            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            PrintLog.print_log(db_version)        
            # close the communication with the PostgreSQL
            cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            PrintLog.print_log(error)
        finally:
            if conn is not None:
                conn.close()
                PrintLog.print_log('Database connection closed.')
    
    # Commands must be a python list
    def execute_commands(self, commands):    
        """
        Function to execute the given list of SQL commands on the database.
        """           
        conn = None
        try:           
            params = self.config()
            PrintLog.print_log('Connecting to the PostgreSQL database')
            conn = psycopg2.connect(**params)
            cur = conn.cursor()
            # create tables            
            for command in commands:
                PrintLog.print_log("\nExecuting:", command)
                cur.execute(command)
            conn.commit()
            cur.close()            
        except (Exception, psycopg2.DatabaseError) as error:
            PrintLog.print_log(error)
        finally:
            if conn is not None:
                PrintLog.print_log('Finished ok.')
                conn.close()
    
    def init_create_tables(self):
        """
        Function to initialise tables if they do not exist in the database.
        """  
        # No PRIMARY KEY since we manage duplicates in other ways
        # Some repos can appear with diferents topics, the databse sld manage those and merge them by topics     
        create_tables = (
            """
            CREATE TABLE IF NOT EXISTS github (
                index BIGINT,
                full_name TEXT,
                description TEXT,
                link TEXT NOT NULL,
                stars INTEGER,
                forks INTEGER,
                watchers INTEGER,
                updated_on TEXT,
                keywords TEXT,
                source TEXT NOT NULL
            )
            """,
            """ 
            CREATE TABLE IF NOT EXISTS gitlab (
                index BIGINT,
                full_name TEXT,
                description TEXT,
                link TEXT  NOT NULL,
                stars INTEGER,
                forks INTEGER,
                updated_on TEXT,
                keywords TEXT,
                source TEXT NOT NULL
            )
            """,
            """ 
            CREATE TABLE IF NOT EXISTS bitbucket (
                index BIGINT,
                full_name TEXT,
                description TEXT,
                link TEXT  NOT NULL,
                watchers INTEGER,
                updated_on TEXT,
                keywords TEXT,
                source TEXT NOT NULL
            )
            """)
        # connect and create        
        self.execute_commands(create_tables)
                    
    def insert_dataframe_into_table(self, table, data):
        """
        Function to insert into a table given the Pandas DataFrame passed as argument using sqlalchemy.
        """
        try:         
            params = self.config()        
            # postgresql://username:password@localhost:5432/mydatabase
            connection = (
            "postgresql://" 
            + params["user"] 
            + ":" + params["password"]
            + "@" + params["host"] 
            + ":" + params["port"]
            + "/" + params["database"]
            )
            # sqlalchemy
            engine = create_engine(connection)
                  
            data.to_sql(table, engine, if_exists='append') # if_exists the table append     
                             
        except (Exception) as error:
            PrintLog.print_log(error)
        finally:
            PrintLog.print_log("Inserted: ", data)
            return
        
    def delete_duplicates(self, table):
        """
        Function to remove duplicates in the table passed as argument.
        """        
        # list of columns that must contain the same data in order to delete duplicates
        github_cols =    "full_name, description, link, stars, forks, watchers, updated_on, keywords, source"
        gitlab_cols =    "full_name, description, link, stars, forks, updated_on, keywords, source"
        bitbucket_cols = "full_name, description, link, watchers, updated_on, keywords, source"
        
        if table == "github":
            cols = github_cols
        elif table == "gitlab":
            cols = gitlab_cols
        elif table == "bitbucket":
            cols = bitbucket_cols
        else:
            return "Select a valid table"

        # ctid points to the physical location of the record in the table
        del_duplicates = [
            (
            """
            DELETE FROM """ + table + """
                WHERE ctid IN (
                    SELECT
                        ctid
                    FROM (
                        SELECT
                            ctid,
                            row_number() OVER w as rnum
                        FROM """ + table + """
                        WINDOW w AS (
                            PARTITION BY """ + cols + """
                            ORDER BY ctid
                        )
                    ) t
                WHERE t.rnum > 1);
            """
            )
        ]        
        self.execute_commands(del_duplicates)