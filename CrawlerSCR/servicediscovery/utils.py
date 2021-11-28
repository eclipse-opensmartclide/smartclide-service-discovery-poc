#!flask/bin/python
# Eclipse Public License 2.0

from datetime import datetime, time
import requests
import logging

# User-Agents are randomized per-session or per-request.
#  a random User-Agent is selected from the list useragents.txt (inside the requests_random_user_agent package)
import requests_random_user_agent


class PrintLog():
    def log(text):
        """
        Using logging and print for log the text recived as argument.
        """
        print(text)
        logging.info(text)
        
class SCRUtils():
    # Service code repo utils
    def get_url(url, header):
        """
        Function request get a url with a custom header, also handles error codes.
        """
        ## TODO: handle more error codes!!
        response = requests.request("GET", url, headers = header)
        
        ## TODO: handle posible infinite loop
        while(response.status_code == 429):  # Error API limit reached ?           
            print("\nRateLimitExceededException")
            print("Sleeping (60s)")
            time.sleep(60)
            # Check again
            response = requests.request("GET", url, headers = header)
            
        return response

    def export_csv(df, path, name, export_index, export_header):
        """
        Function to export a DataFrame in the path, with a name + timestamp, and export index and/or header
        """
        # Try?
        df.to_csv(path + name + '_' + datetime.now().strftime('%d_%m_%Y') + '.csv',
            index=export_index,
            header=export_header)
# flask errors    
class FlaskUtils():

    def handle400error(ns, message):
        """
        Function to handle a 400 (bad arguments code) error.
        """
        return ns.abort(400, status=message, statusCode="400")

    def handle404error(ns, message):
        """
        Function to handle a 404 (not found) error.
        """
        return ns.abort(404, status=message, statusCode="404")

    def handle500error(ns):
        """
        Function to handle a 500 (unknown) error.
        """
        message = "Unknown error, please contact administrator."
        return ns.abort(500, status=message, statusCode="500")