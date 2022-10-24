import json
import pandas as pd
from dateutil import parser
import os
import pathlib
from werkzeug.utils import secure_filename
from datetime import datetime


def get_filename(name, extension):
    scrap_date = get_today_datetime()
    filename = name + '_' + scrap_date + '.' + extension
    return filename

def get_today_datetime():

    now = datetime.now()
    #dt_string = now.strftime("%d_%m_%Y_%H_%M")
    dt_string = now.strftime("%d_%m_%Y")
    return dt_string




def get_api_key():
    with open('api_key.json') as client_secrets_file:
        client_secrets = json.load(client_secrets_file)
    if client_secrets:
        return client_secrets["key"]
    else:
        return None


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


def get_query():
    with open('config.json') as config_file:
        config_file = json.load(config_file)
    if config_file:
        q = config_file["keywords"]
        return q
    return None



def convert_to_local_zone(datestring):
    try:
        utc_dt = parser.parse(datestring)
        local_dt = utc_dt.astimezone(None)
        date_time = local_dt.strftime("%Y-%m-%d, %H:%M:%S")
        return date_time
    except:
        return datestring


def export_dict_to_excel(records, directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)

    df = pd.DataFrame(records).T
    df.to_excel(filename_path)


def export_dict_to_csv(records, directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)

    df = pd.DataFrame(records).T
    df.to_csv(filename_path)





