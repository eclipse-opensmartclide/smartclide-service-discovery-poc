# -*- coding: utf-8 -*-
#
# Copyright (c) 2021 AIR Institute - David Berrocal @dabm-git
#
# This file is part of SmartCLIDE 
# (see  https://smartclide.eu/)
#
#
# This program is distributed under Eclipse Public License 2.0
# (see https://github.com/dabm-git/Service-discovery/blob/main/LICENSE/)
#
#
#

""" Programableweb

!pip install requests-random-user-agent
!pip install pandas
!pip install bs4
!pip install lxml

"""
import time
from datetime import datetime
import os
import glob
from pathlib import Path
import pandas as pd
import numpy as np
import concurrent.futures
import requests
import requests_random_user_agent
from bs4 import BeautifulSoup
import re

pd.options.mode.chained_assignment = None
# List url processing


class ProgWeb:
    @staticmethod
    def _download_list(urlsSplited):
        """
        Iterates over the input list and accesses the url 
        to collect data using requests and BeautifulSoup

        :param urlsSplited: list
        :return DataFrame:
        """
        df_temp = pd.DataFrame()

        for url in urlsSplited:
            
            time.sleep(0.1) # More?

            rq = requests.get(url, allow_redirects=False)

            while rq.status_code == 429:  # Too many rq
                time.sleep(3600)  # 1h TODO: hanlde time
                rq = requests.get(url, allow_redirects=False)
                if rq.status_code == 200:
                    break

            main_data = rq.text
            # dataset from table
            df_url = pd.read_html(main_data, index_col=0)[0]

            main_soup = BeautifulSoup(main_data, 'html.parser')
            main_names = main_soup.find_all('tr')[1:245]

            list_url = []
            # Head url for meta_url
            meta_Url = 'https://www.programmableweb.com'

            for row in main_names:
                text = row.find_all('td')[0]
                list_url.append((meta_Url + str(text).partition('<a href="')
                                [2].partition('">')[0]))  # URL to specific page

            df_url['Meta_Url'] = list_url

            df_temp = df_temp.append(df_url, ignore_index=True)

        return df_temp

    @staticmethod
    def download_list(url, numPages, numWorkers, listName, forceListUpdate):
        """
        Creates a DataFrame list from listName (programmableweb URL)
        and exports the set of urls if this set is not present will be downloaded

        :param url: str
        :param numPages: int
        :param numWorkers: int
        :param listName: str
        :param forceListUpdate: int
        :return DataFrame:
        """
        # Have we a list file?
        df_temp = Utils.find_local_csv(listName)

        if df_temp.empty or forceListUpdate == True:
            print("List file " + listName +
                  " not found or force updated, downloading now.")

            urls = []
            # Generate the new list
            for i in range(numPages):
                main_url = url + str(i)
                urls.append(main_url)

            # Split urls
            urls_splited = np.array_split(
                urls, numWorkers)  # max workers = num splits

            # Remove empty lists from the split
            #urls_splited = [i for i in urls_splited if i]
            #urls_splited = list(filter(None, urls_splited))

            tasks = []

            with concurrent.futures.ThreadPoolExecutor(len(urls_splited)) as executor:
                for split in range(len(urls_splited)):
                    # print("task launched for list")
                    tasks.append(executor.submit(
                        ProgWeb._download_list, urls_splited[split]))

                # Union
                for result in tasks:
                    df_temp = df_temp.append(result.result())

            # Export the metacsv for handle updates
            print("List " + listName + " generated at: ", str(FILES_PATH))

            df_temp = df_temp.reset_index(drop=True)

            df_temp.to_csv(str(FILES_PATH) + '/' + listName + '_' +
                           datetime.now().strftime('%d_%m_%Y') + '.csv', index=True, header=True)

        print("List found, downloading meta urls.")
        return df_temp

    # Meta url processing
    @staticmethod
    def _download_meta_url(df_temp, batchName, isAPI2):
        """
        Iterates over the input dataframe and accesses the metaurl 
        to collect data based in listType imput using requests and BeautifulSoup

        :param df_temp: DataFrame
        :param batchName: str
        :param isAPI2: int
        :return DataFrame:
        """

        df_temp = df_temp.reset_index(drop=True)

        # Drop rows with empty Meta_Url or Meta_Meta_Urls
        for i in range(len(df_temp)):

            if isAPI2:
                meta_url = df_temp['Meta_Meta_Url'][i]
            else:
                meta_url = df_temp['Meta_Url'][i]

            time.sleep(1)  # sleep random?
            rq = requests.get(meta_url, allow_redirects=False)

            while rq.status_code == 429:  # Too many rq
                time.sleep(3600)  # 1h TODO: hanlde time
                rq = requests.get(meta_url, allow_redirects=False)
                if rq.status_code == 200:
                    break
                # Sleep?, proxy change?, user agent change?

            meta_data = rq.text
            meta_soup = BeautifulSoup(meta_data, 'html.parser')

            # Update Description from the meta url
            #   api-library LIB_BATCH do not have description
            if batchName == LIB_BATCH:
                df_temp['Description'] = ""
                meta_description = ""
            elif batchName == MASH_BATCH:
                meta_description = str(meta_soup.find('div', class_='tabs-header_description')).partition(
                    '">')[2].partition('</')[0].partition('">')[2].partition('">')[2].partition('">')[2]
            else:  # CODE, SDK, FRAME, API
                meta_description = str(meta_soup.find(
                    'div', class_='tabs-header_description')).partition('">')[2].partition('</div>')[0]

            # unicode escaping
            df_temp['Description'][i] = [
                bytes(meta_description, 'utf-8').decode('unicode_escape')]

            # API and we dont have the meta meta url
            if (batchName == API_BATCH) and (df_temp['Meta_Meta_Url'][i] == ""):
                meta_specs = meta_soup.find(id='version-details-field')
                # If meta_specs here is None the page have redericted the rq
                #   so we ignore it because progweb mark them as Deactivated and no info is given
                if (meta_specs == None):
                    continue

                selected = meta_specs.select("div")
                # href?
                if (str(selected).find("href=") > -1):
                    # select the text btw href=" text "
                    r1 = re.findall(r"href ?= ?.(.*?)\"", str(selected))
                    if (len(r1) < 0):
                        # print("empty")
                        continue
                    else:
                        # r1[-1] in case we have multiple entries in the list select the last one
                        # ex> https://www.programmableweb.com/api/twitter
                        df_temp['Meta_Meta_Url'][i] = "https://www.programmableweb.com" + r1[-1]
                        continue

            else:
                # Get section specs and iterate the labels
                meta_specs = meta_soup.find('div', class_='section specs')
                if (meta_specs == None):
                    continue
                selected = meta_specs.select("label")
               

            if selected == None:
                continue

            for lab in selected:

                if batchName == MASH_BATCH:
                    # Search for Related APIs
                    if (lab.text.lower().find("related apis") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Related APIs'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Categories
                    if (lab.text.lower().find("categories") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Categories'][i] = lab.find_next_sibling().text
                        continue

                    # Search for URL
                    if (lab.text.lower().find("url") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['URL'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Company
                    if (lab.text.lower().find("company") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Company'][i] = lab.find_next_sibling().text
                        continue

                    # Search for App Type
                    if (lab.text.lower().find("app type") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['App Type'][i] = lab.find_next_sibling().text
                        continue
                    continue

                if batchName == SDK_BATCH:
                    # Search for Related APIs
                    if (lab.text.lower().find("related apis") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Related APIs'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Languages
                    if (lab.text.lower().find("languages") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Languages'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Categories and remplace them
                    if (lab.text.lower().find("categories") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Category'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Provider
                    if (lab.text.lower().find("sdk provider") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Provider'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Provider
                    if (lab.text.lower().find("url") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Asset URL'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Provider
                    if (lab.text.lower().find("repository") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Repository'][i] = lab.find_next_sibling().text
                        continue
                    continue

                if batchName == FRAME_BATCH:
                    # Search for Languages
                    if (lab.text.lower().find("languages") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Languages'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Provider
                    if (lab.text.lower().find("provider") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Provider'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Asset URL
                    if (lab.text.lower().find("asset home") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Asset URL'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Repository
                    if (lab.text.lower().find("repository") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Repository'][i] = lab.find_next_sibling().text
                        continue

                    # Search for TOS
                    if (lab.text.lower().find("terms of service") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Terms Of Service'][i] = lab.find_next_sibling().text
                        continue
                    continue

                if batchName == CODE_BATCH:
                    # Search for Repo
                    if (lab.text.lower().find("repository") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Repository'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Source Code
                    if (lab.text.lower().find("link to source code") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Source Code'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Categories and remplace them
                    if (lab.text.lower().find("categories") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Category'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Languages
                    if (lab.text.lower().find("languages") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Languages'][i] = lab.find_next_sibling().text
                        continue
                    continue

                if batchName == LIB_BATCH:
                    # Search for Related APIs
                    if (lab.text.lower().find("related apis") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Related APIs'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Languages
                    if (lab.text.lower().find("languages") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Languages'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Framework
                    if (lab.text.lower().find("related framework") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Related Frameworks'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Categories and remplace them
                    if (lab.text.lower().find("categories") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Category'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Architectural
                    if (lab.text.lower().find("architectural style") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Architectural Style'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Provider
                    if (lab.text.lower().find("library provider") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Provider'][i] = lab.find_next_sibling().text
                        continue
                    # Search for URL
                    if (lab.text.lower().find("asset home") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Asset URL'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Provider
                    if (lab.text.lower().find("repository") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Repository'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Provider
                    if (lab.text.lower().find("terms of service") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Terms Of Service'][i] = lab.find_next_sibling().text
                        continue
                    # Search for Provider
                    if (lab.text.lower().find("type") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Type'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Provider
                    if (lab.text.lower().find("docs home") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Docs Home'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Provider
                    if (lab.text.lower().find("request formats") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Request Formats'][i] = lab.find_next_sibling().text
                        continue

                    # Search for Provider
                    if (lab.text.lower().find("response formats") > -1):
                        #print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Response Formats'][i] = lab.find_next_sibling().text
                        continue
                    continue

                if batchName == API_BATCH:
                    # META META URL data
                    if (lab.text.lower().find("endpoint") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Endpoint'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("portal") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Portal'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("primary") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Category'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("secondary") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        secondary = lab.find_next_sibling().text
                        df_temp['Category'][i] = (
                            df_temp['Category'][i] + secondary)
                        continue

                    if (lab.text.lower().find("provider") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Provider'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("authentication ") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Authentication'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("version status") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Version status'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("version") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Version'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("type") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Type'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("architectural ") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Architectural'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("request formats") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Request Formats'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("response formats") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Response Formats'][i] = lab.find_next_sibling().text
                        continue

                    if (lab.text.lower().find("unofficial") > -1):
                        # print(lab.text + ": " + lab.find_next_sibling().text)
                        df_temp['Unofficial'][i] = lab.find_next_sibling().text
                        continue

        print("List " + batchName + " generated at: ",
              str(FILES_PATH) + "\\" + batchName)

        # Export the metacsv for handle updates
        df_temp.to_csv(str(FILES_PATH) + '/' + batchName + '/_' + str(len(df_temp)) + "_" + batchName + "_" +
                       datetime.now().strftime('%H_%M_%S_%f__%d_%m_%Y') + '.csv', index=True, header=True)

        return df_temp

    @staticmethod
    def download_meta_url(df, numSplits, listType, batchName, isAPI):
        """
        Splits a dataframe and uses simultaneous executions to access the metaurl
        wirh _download_meta_url the information is collected and returned reseting the index

        :param df: DataFrame
        :param numSplits: int
        :param listType: str
        :param batchName: str
        :param isAPI: int
        :return DataFrame:
        """

        df_temp = pd.DataFrame()

        # Split dataframe
        dt_splited = np.array_split(df, numSplits)  # max workers

        # Remove empty dataframes from the split
        dt_splited = list(filter(lambda df: not df.empty, dt_splited))

        # Batch folder to store the splits
        Utils.create_relative_folder(batchName)

        tasks = []

        with concurrent.futures.ThreadPoolExecutor(len(dt_splited)) as executor:
            # Download splited dataframes with jobs
            for split in range(len(dt_splited)):
                # print("task launched")
                tasks.append(executor.submit(
                    ProgWeb._download_meta_url, dt_splited[split], batchName, not isAPI))

            # Union
            for result in tasks:
                df_temp = df_temp.append(result.result())

        df_temp = df_temp.reset_index(drop=True)

        # Export the union of the splits
        if not isAPI:
            df_temp.to_csv(str(FILES_PATH) + '/' + listType + '_' +
                           datetime.now().strftime('%d_%m_%Y') + '.csv', index=True, header=True)

        return df_temp

    @staticmethod
    def getNumPages(headUrl):
        """
        Return the num of pages which has data in the head url 

        :param headUrl: string
        :return int:
        """
        rq = requests.get(headUrl, allow_redirects=False)

        while rq.status_code == 429:  # Too many rq
            time.sleep(3600)  # 1h TODO: hanlde time
            rq = requests.get(headUrl, allow_redirects=False)
            if rq.status_code == 200:
                break
            # Sleep?, proxy change?, user agent change?, more error codes?

        meta_data = rq.text
        meta_soup = BeautifulSoup(meta_data, 'html.parser')

        numPages = str(meta_soup.find('li', class_='pager-next')).partition(
            '">')[2].partition('</')[0].partition('">')[2].partition('</')[0]

        return int(numPages)


class Utils:
    # Utils
    @staticmethod
    def create_relative_folder(folderName):
        """
        Creates a folder folderName in the relative path

        :param folderName: string
        """
        os.makedirs(os.path.join(Path(__file__).parent,
                    folderName), exist_ok=True)

    @staticmethod
    def find_local_csv(fileName):
        """
        Tryes to find a filename*.csv file to import and return it as DataFrame

        :param fileName: string
        :return DataFrame:
        """
        # Relative
        os.chdir(Path(__file__).parent)
        name = glob.glob(fileName + '*.csv')
        # grab the 1th file
        if len(name) > 0:
            return pd.read_csv(name[0], index_col=[0])
        else:
            return pd.DataFrame()

# DW


def download_data(dataType, url, numPages, numWorkers, listName, batchName, forceListUpdate):
    """
    Creates a DataFrame from dataType programmableweb URL
     and exports the dataframe gererated from download_list set of urls
     if this set is not present will be downloaded

    :param dataType: str
    :param url: str
    :param numPages: int
    :param numWorkers: int
    :param listName: str
    :param batchName: str
    :param forceListUpdate: Bool
    :return DataFrame:
    """
    df_temp = ProgWeb.download_list(url, numPages, numWorkers,
                                    listName, forceListUpdate)
    
    # time.sleep(120)  # ?

    # Creates new columns based on type
    if dataType == FRAME_TYPE:
        df_temp['Languages'] = ""
        df_temp['Provider'] = ""
        df_temp['Asset URL'] = ""
        df_temp['Repository'] = ""
        df_temp['Terms Of Service'] = ""
    elif dataType == CODE_TYPE:
        df_temp['Source Code'] = ""
        df_temp['Repository'] = ""
        df_temp['Languages'] = ""
    elif dataType == SDK_TYPE:
        df_temp['Description'] = ""
        df_temp['Repository'] = ""
        df_temp['Languages'] = ""
        df_temp['Provider'] = ""
        df_temp['Asset URL'] = ""
    elif dataType == LIB_TYPE:
        df_temp['Languages'] = ""
        df_temp['Related Frameworks'] = ""
        df_temp['Category'] = ""
        df_temp['Architectural Style'] = ""
        df_temp['Provider'] = ""
        df_temp['Asset URL'] = ""
        df_temp['Repository'] = ""
        df_temp['Terms Of Service'] = ""
        df_temp['Type'] = ""
        df_temp['Docs Home'] = ""
        df_temp['Request Formats'] = ""
        df_temp['Response Formats'] = ""
    elif dataType == MASH_TYPE:
        df_temp['Related APIs'] = ""
        df_temp['Categories'] = ""
        df_temp['URL'] = ""
        df_temp['Company'] = ""
        df_temp['App Type'] = ""
    elif dataType == API_TYPE:
        df_temp['Meta_Meta_Url'] = ""
        df_temp['Category'] = ""
        df_temp['Endpoint'] = ""
        df_temp['Portal'] = ""
        df_temp['Provider'] = ""
        df_temp['Authentication'] = ""
        df_temp['Version'] = ""
        df_temp['Version status'] = ""
        df_temp['Type'] = ""
        df_temp['Architectural'] = ""
        df_temp['Request Formats'] = ""
        df_temp['Response Formats'] = ""
        df_temp['Unofficial'] = ""

        print("download_meta_meta_url API")        
        # First call to get the meta meta URL, 2 call to get the data
        df_temp = ProgWeb.download_meta_url(
            df_temp, numWorkers, dataType, batchName, 1)

        df_temp.to_csv(str(FILES_PATH) + '/' + dataType + '_Meta2Url_' +
                       datetime.now().strftime('%d_%m_%Y') + '.csv', index=True, header=True)

     # If is API TYPE here we dw the Meta_Meta_Url
    if dataType == API_TYPE:
        # If Meta_Meta_Url here is None the page have redericted the rq
        #   so we ignore it because progweb mark them as Deactivated and no info is given
        df_temp['Meta_Meta_Url'].replace('', np.nan, inplace=True)
        df_temp.dropna(subset=['Meta_Meta_Url'], inplace=True)

    # Just in case we dont have meta URL, drop the row
    df_temp['Meta_Url'].replace('', np.nan, inplace=True)
    df_temp.dropna(subset=['Meta_Url'], inplace=True)

    print("download_meta_url")
    df_temp = ProgWeb.download_meta_url(
        df_temp, numWorkers, dataType, batchName, 0)

    return df_temp

# CONSTANTS

# Relative path
FILES_PATH = Path(__file__).parent

LIB_URL = "https://www.programmableweb.com/category/all/api-library?page="
LIB_PAGES = ProgWeb.getNumPages(LIB_URL)  # 67
LIB_LIST = "LIB_list"
LIB_BATCH = "LIB_batch"
LIB_TYPE = "LIB"

MASH_URL = "https://www.programmableweb.com/category/all/mashups?page="
MASH_PAGES = ProgWeb.getNumPages(MASH_URL)  # 258
MASH_LIST = "MASH_list"
MASH_BATCH = "MASH_batch"
MASH_TYPE = "MASH"

FRAME_URL = "https://www.programmableweb.com/category/all/web-development-frameworks?page="
FRAME_PAGES = ProgWeb.getNumPages(FRAME_URL)  # 23
FRAME_LIST = "FRAME_list"
FRAME_BATCH = "FRAME_batch"
FRAME_TYPE = "FRAME"

CODE_URL = "https://www.programmableweb.com/category/all/sample-source-code?page="
CODE_PAGES = ProgWeb.getNumPages(CODE_URL)  # 616
CODE_LIST = "CODE_list"
CODE_BATCH = "CODE_batch"
CODE_TYPE = "CODE"

SDK_URL = "https://www.programmableweb.com/category/all/sdk&page="
SDK_PAGES = ProgWeb.getNumPages(SDK_URL)  # 776
SDK_LIST = "SDK_list"
SDK_BATCH = "SDK_batch"
SDK_TYPE = "SDK"

API_URL = "https://www.programmableweb.com/category/all/apis?page="
API_PAGES = ProgWeb.getNumPages(API_URL)  # 892
API_LIST = "API_list"
API_BATCH = "API_batch"
API_TYPE = "API"

"""### Wait btw types to avoid 429
TODO?: handle 429 with proxys?

"""

# print("\nFRAME")
# df_frame = download_data(FRAME_TYPE, FRAME_URL, FRAME_PAGES, 20,
#                          FRAME_LIST, FRAME_BATCH, False)
# time.sleep(3600)  # 1h

# print("\nLIB")
# df_frame = download_data(LIB_TYPE, LIB_URL, LIB_PAGES, 20,
#                          LIB_LIST, LIB_BATCH, False)
# time.sleep(3600)  # 1h

# print("\nSDK")
# df_frame = download_data(SDK_TYPE, SDK_URL, SDK_PAGES, 20,
#                          SDK_LIST, SDK_BATCH, True)
# time.sleep(3600)  # 1h

# print("\nMASH")
# df_frame = download_data(MASH_TYPE, MASH_URL, MASH_PAGES, 20,
#                          MASH_LIST, MASH_BATCH, False)
# time.sleep(3600)

# print("\nCODE")
# df_frame = download_data(CODE_TYPE, CODE_URL, CODE_PAGES, 20,
#                          CODE_LIST, CODE_BATCH, False)
# time.sleep(3600)

# print("\nAPI")
# df_api = download_data(API_TYPE,
#                        API_URL, 
#                        API_PAGES,
#                        30, # Num threads
#                        API_LIST, 
#                        API_BATCH,
#                        False) # Force Update List
# print("\nFin")
