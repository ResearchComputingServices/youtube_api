import json
import pandas as pd
from dateutil import parser
import os
import pathlib
from werkzeug.utils import secure_filename
from datetime import datetime
import sys
import traceback

#*****************************************************************************************************
#Read a excel file given as a parameter and if specific columns are provided those are extracted from
#the file.
#The file is returned as a data frame
#*****************************************************************************************************
def read_excel_file_to_data_frame(filename, columns=None):
    # Load file
    df = None
    success = False
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
#Read a excel file given as a parameter and if specific columns are provided those are extracted from
#the file.
#The file is returned as a dictionary
#*****************************************************************************************************
def read_excel_file_to_dict_old(filename, columns=None):
    dict=None
    df, success = read_excel_file_to_data_frame(filename, columns=None)
    if success:
        dict = df.T.to_dict()
    return dict


#*****************************************************************************************************
def read_excel_file_to_dict(filename, index=None):
    dict=None
    df, success = read_excel_file_to_data_frame(filename)
    if success:
        if index:
            dict = df.set_index(index).T.to_dict()
        else:
            dict = df.T.to_dict()
    return dict


#*****************************************************************************************************
#This functions creates a filename with the following format
#NAME_TODAY_DATE_EXTENSION
#*****************************************************************************************************
def get_filename(name, extension):
    scrap_date = get_today_datetime()
    #filename = name + '_' + scrap_date + '.' + extension
    filename = scrap_date + '_' + name + '.' + extension
    return filename


#*****************************************************************************************************
#Gets the current date
#*****************************************************************************************************
def get_today_datetime():
    now = datetime.now()
    #dt_string = now.strftime("%d_%m_%Y_%H_%M")
    #dt_string = now.strftime("%d_%m_%Y")
    dt_string = now.strftime("%Y_%m_%d")
    return dt_string

#*****************************************************************************************************
#Gets the API key from the config file
#*****************************************************************************************************
def get_api_key():
    try:
        with open('api_key.json') as client_secrets_file:
            client_secrets = json.load(client_secrets_file)
        if client_secrets:
            return client_secrets["key"]
        else:
            return None
    except:
        print("File api_key.json couldn't be loaded. Please verify this file.")
    return None

#*****************************************************************************************************
#Gets the URL link for the playlist
#*****************************************************************************************************
def get_url_playlist():
    try:
        with open('config.json') as config_file:
            config_file = json.load(config_file)
        if config_file:
            pl = config_file["playlist"]
            index = pl.find("list=")
            if index:
                playlist = pl[index+5:]
                return playlist
    except:
        print ("File config.json couldn't be loaded. Please verify this file.")
    return None

#*****************************************************************************************************
#Gets the query to be executed in the API search
#*****************************************************************************************************
def get_query():
    try:
        with open('config.json') as config_file:
            config_file = json.load(config_file)
        if config_file:
            q = config_file["query"]
            return q
        return None
    except:
        print("File config.json couldn't be loaded. Please verify this file.")
    return None


#*****************************************************************************************************
#This functions converts a UTC date to the local zone
#Returns date as a string
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
#This functions converts a UTC date to the local zone
#Returns date as a date time object
#*****************************************************************************************************
def convert_to_local_zone_dt(datestring):
    try:
        utc_dt = parser.parse(datestring)
        local_dt = utc_dt.astimezone(None)
        return local_dt
    except:
        return None

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



#-----------------------------------------------------------------------------------------------------------------------
#This function retrieves a list of ids from a file
#-----------------------------------------------------------------------------------------------------------------------
def get_ids_from_file(filename, id_column):
    try:
        ids = None
        #Load file
        df, success = read_excel_file_to_data_frame(filename,[id_column])
        if success:
            #Convert to list
            dfT = df.T
            idsl = dfT.values.tolist()
            #ids = list(set(idsl[0]))
            ids = idsl[0]
    except:
        print("Error on get_ids_from_file. Verify input file and header id")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return ids






