import json
import pandas as pd
from dateutil import parser
import os
import pathlib
from werkzeug.utils import secure_filename
from datetime import datetime

#*****************************************************************************************************
#Read a excel file given as a parameter and if specific columns are provided those are extracted from
#the file.
#The file is returned as a data frame
#*****************************************************************************************************
def read_excel_file_to_data_frame(filename, columns=None):
    # Load file
    df = None
    sucess = False
    try:
        if filename:
            # filename = os.path.join(directory, filename)
            abs_path = pathlib.Path().resolve()
            filename_fullpath = os.path.join(abs_path, filename)
            data = pd.read_excel(filename_fullpath)
            if columns:
                try:
                    df = pd.DataFrame(data, columns=columns)
                except:
                    df = pd.DataFrame(data)
            else:
                df = pd.DataFrame(data)
            success = True
    except:
        print ("Error reading file: " + filename)
        print ("Please, verify if file exists.")
        df = None

    return df, success


#*****************************************************************************************************
#This functions creates a filename with the following format
#NAME_TODAY_DATE_EXTENSION
#*****************************************************************************************************
def get_filename(name, extension):
    scrap_date = get_today_datetime()
    filename = name + '_' + scrap_date + '.' + extension
    return filename


#*****************************************************************************************************
#Gets the current date
#*****************************************************************************************************
def get_today_datetime():
    now = datetime.now()
    #dt_string = now.strftime("%d_%m_%Y_%H_%M")
    dt_string = now.strftime("%d_%m_%Y")
    return dt_string

#*****************************************************************************************************
#Gets the API key from the config file
#*****************************************************************************************************
def get_api_key():
    with open('api_key.json') as client_secrets_file:
        client_secrets = json.load(client_secrets_file)
    if client_secrets:
        return client_secrets["key"]
    else:
        return None

#*****************************************************************************************************
#Gets the URL link for the playlist
#*****************************************************************************************************
def get_url_playlist():
    with open('config.json') as config_file:
        config_file = json.load(config_file)
    if config_file:
        pl = config_file["playlist"]
        index = pl.find("list=")
        if index:
            playlist = pl[index+5:]
            return playlist
    return None

#*****************************************************************************************************
#Gets the query to be executed in the API search
#*****************************************************************************************************

def get_query():
    with open('config.json') as config_file:
        config_file = json.load(config_file)
    if config_file:
        q = config_file["query"]
        return q
    return None


#*****************************************************************************************************
#This functions converts a UTC date to the local zone
#*****************************************************************************************************
def convert_to_local_zone(datestring):
    try:
        utc_dt = parser.parse(datestring)
        local_dt = utc_dt.astimezone(None)
        date_time = local_dt.strftime("%Y-%m-%d, %H:%M:%S")
        return date_time
    except:
        return datestring

#*****************************************************************************************************
#This functions exports a dictionary to a excel file with filename given as a parameter
#*****************************************************************************************************
def export_dict_to_excel(records, directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)
    df = pd.DataFrame(records).T
    df.to_excel(filename_path)
    return filename_path


#*****************************************************************************************************
#This functions exports a dictionary to a csv file with filename given as a parameter
#*****************************************************************************************************
def export_dict_to_csv(records, directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)

    df = pd.DataFrame(records).T
    df.to_csv(filename_path)

    return filename_path

#*****************************************************************************************************
#This functions exports a data fraeme to a excel file with filename given as a parameter
#*****************************************************************************************************
def export_dataframe_to_excel(records, directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)

    df = records.T
    df.to_excel(filename_path)




