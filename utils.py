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



#****************************************************************************************************
#This function checks if a file exists with a given name.
#It returns a filename with the highest counter
#****************************************************************************************************
def _get_latest_file(directory,prefix, extension='.xlsx'):

    latest_number = -1

    for file in os.listdir(directory):
        if file.startswith(prefix):
            name = file
            only_name = name.split(extension)[0];
            st = only_name.split('_')
            last_st = st[len(st)-1]
            try:
                number = int(last_st)
                if number > latest_number:
                    latest_number = number
            except:
                if latest_number < 0:
                    latest_number = 0

    return (latest_number)

#-----------------------------------------------------------------------------------------------------------------------
#This function returns a name of a file and a counter if the name already exists
#-----------------------------------------------------------------------------------------------------------------------
def get_filename_ordered(directory, name, extension):
    scrap_date = get_today_datetime()
    filename = scrap_date + '_' + name + '.' + extension
    number = _get_latest_file(directory,secure_filename(scrap_date + '_' + name), '.'+extension)
    if number>=0:
        filename = scrap_date + '_' + name + '_' + str(number+1) + '.' + extension
    return secure_filename(filename)



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
#Gets the id of a playslit from the url
#*****************************************************************************************************
def get_playlist_id(url):
    try:
        index = url.find("list=")
        if index>=0:
            playlist = url[index + 5:]
        return playlist
    except:
        print("Invalid URL")
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
    #df = df.applymap(lambda x: x.encode('unicode_escape').
    #                               decode('utf-8') if isinstance(x, str) else x)
    df.to_excel(filename_path, engine='xlsxwriter')
    df.to_excel(filename_path)
    return filename_path


#*****************************************************************************************************
#This functions exports a dictionary to a csv file with filename given as a parameter
#*****************************************************************************************************
def export_dict_to_csv(records, directory, name, mode='w', index=True, header=True):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)

    df = pd.DataFrame(records).T
    df.to_csv(filename_path, mode=mode, index=index, header=header)

    return filename_path

#*****************************************************************************************************
#This functions exports a dictionary to a csv file with filename given as a parameter
#*****************************************************************************************************
def get_fullpath(directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)
    return filename_path


#*****************************************************************************************************
#This functions exports a csv file to an excel file
#*****************************************************************************************************
def export_csv_to_excel(csv_file, excel_file):

    # reading the csv file
    csv_dataframe = pd.read_csv(csv_file)

    # creating an output excel file
    result_excelfile = pd.ExcelWriter(excel_file)

    # converting the csv file to an excel file
    csv_dataframe.to_excel(result_excelfile, index=False)

    # saving the excel file
    result_excelfile.save()

#*****************************************************************************************************
#This functions exports a dictionary to a csv file with filename given as a parameter
#*****************************************************************************************************
def export_dict_to_csv_1(records, directory, name):
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
    return filename_path


#*****************************************************************************************************
#This functions exports a data frame to a excel file with filename given as a parameter
#Columsn are specified as parameter
#*****************************************************************************************************
def export_list_to_excel(lst, directory, name, columns):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)
    df = pd.DataFrame(lst, columns=columns)
    df.to_excel(filename_path)
    return filename_path

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

#***********************************************************************************************************************
#***********************************************************************************************************************
def delete_file(file):
    if (os.path.isfile(file)):
        os.remove(file)

#***********************************************************************************************************************
#***********************************************************************************************************************
def remove_prefix_url(url):
    #Attempt to remove https from url
    only_link = url
    try:
        prefix = 'https://'
        if url.startswith(prefix):
            only_link = url.split(prefix)[1];
        else:
            prefix = 'http://'
            if url.startswith(prefix):
                only_link = url.split(prefix)[1];
    except:
        only_link = url

    return only_link





