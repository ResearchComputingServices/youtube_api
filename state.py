import pickle
import pathlib
import os
from werkzeug.utils import secure_filename
from utils import export_list_to_excel
from utils import read_excel_file_to_dict
import sys
import traceback
import math
import pandas as pd

#Requests quotes
#From https://developers.google.com/youtube/v3/determine_quota_cost
#Check regularly for updates.
#We only include the ones we are using

#resource	method	cost
#activities   list	1
#channels     list	1
#comments     list	1
#commentThreads list	1
#playlistItems  list	1
#playlists      list	1
#search         list	100
#videos         list	1


UNITS_ACTIVITIES_LIST = 1
UNITS_CHANNELS_LIST = 1
UNITS_COMMENTS_LIST = 1
UNITS_COMMENTS_THREADS_LIST = 1
UNITS_PLAYLIST_ITEMS_LIST = 1
UNITS_PLAYLIST_LIST = 1
UNITS_SEARCH_LIST = 100
UNITS_VIDEOS_LIST = 1
UNITS_QUOTE_LIMIT = 10000

MAX_JOIN_VIDEOS_IDS = 50
MAX_CHANNELS_PER_REQUEST = 50
MAX_COMMENTS_PER_REQUEST = 100
MAX_REPLIES_PER_REQUEST = 100
MAX_VIDEOS_PER_REQUEST= 50
MAX_PLAYLISTITEMS_PER_REQUEST = 50
MAX_SEARCH_RESULTS_PER_REQUEST = 50
DEFAULT_VIDEOS_TO_RETRIEVE = 200
MAX_VIDEOS_TO_RETRIEVE = 500
MAX_PAGES_SEARCHES = 10   #Each page of 50 results (500 units at most)

ACTION_RETRIEVE_VIDEOS = "retrieve_videos"
ACTION_RETRIEVE_COMMENTS = "retrieve_comments"
ACTION_CREATE_NETWORK = "create_network"
ACTION_RETRIEVE_CHANNELS_METADATA = "retrieve_channels_metadata"
ACTION_RETRIEVE_CHANNELS_ACTIVITY = "retrieve_channels_activity"
ACTION_RETRIEVE_CHANNELS_ALL_VIDEOS = "retrieve_channels_all_videos"

LIST_VIDEOS_TO_MERGE = "videos_files_to_merge"
LIST_COMMENTS_TO_MERGE = "comments_files_to_merge"
LIST_SUBCOMMENTS_TO_MERGE = "subcomments_files_to_merge"
LIST_ACTIONS ="actions"
LIST_CHANNELS_TO_MERGE = "channels_files_to_merge"

VIDEOS_IDS_FILE = "videos_ids_file"
CHANNELS_IDS_FILE = "channels_ids_file"
COMMENTS_COUNT_FILE = "videos_comments_count_file"
VIDEO_INDEX = "video_index"
COMMENT_INDEX = "comment_index"
CHANNEL_INDEX = "channel_index"
NETWORK_FILE = "network_file"
VIDEOS_MERGED = "videos_merged"
COMMENTS_MERGED = "comments_merged"
CHANNELS_MERGED = "channels_merged"
QUOTE_USAGE = "quote_usage"
ALL_VIDEOS_RETRIEVED = "all_videos_retrieved"
ALL_COMMENTS_RETRIEVED = "all_comments_retrieved"
ALL_CHANNELS_RETRIEVED = "all_channels_retrieved"

STATE_DIRECTORY = "state"
STATE_FILENAME = "state.pkl"

SAFETY_BACKUP = 0


state_yt = { "api_key" : "",
              "quote_usage"  : 0,
              "actions" : [],
              "videos_ids_file" : "",
              "channels_ids_file" : "",
              "videos_comments_count_file" : None,
              "videos_files_to_merge" : [],
              "videos_merged" : "",
              "comments_files_to_merge" : [],
              "comments_merged" : "",
              "subcomments_files_to_merge" : [],
              "subcomments_merged" : "",
              "channels_files_to_merge" : [],
              "channels_merged" : "",
              "network_file": "",
              "video_index" : 0,
              "comment_index" : 0,
              "channel_index" : 0,
              "all_videos_retrieved" : False,
              "all_comments_retrieved": False,
              "all_channels_retrieved": False,
           }

def get_fullpath(directory, name):
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)
    return filename_path

def save_state_to_file(state):
    directory = STATE_DIRECTORY
    name = STATE_FILENAME
    filename_path = get_fullpath(directory, name)
    with open(filename_path, 'wb') as file:
        pickle.dump(state, file)

def load_state_from_file():
    obj = None
    directory = STATE_DIRECTORY
    name = STATE_FILENAME
    file = get_fullpath(directory,name)
    if os.path.exists(file):
        with open(file, 'rb') as f:
            obj = pickle.load(f)
    return obj

def set_quote_usage(state, value):
    state["quote_usage"] = value
    save_state_to_file(state)
    return state

def update_quote_usage(state, value):
    state["quote_usage"] = state["quote_usage"] + value
    save_state_to_file(state)
    return state

def set_api_key(state, value):
    state["api_key"] = value
    save_state_to_file(state)
    return state

def add_action(state, action):
    if action and action not in state["actions"]:
        state["actions"].append(action)
        save_state_to_file(state)
    return state

def remove_action(state, action=None, all=None):
    if action and action in state["actions"]:
        state["actions"].remove(action)
    if all:
        state["actions"] = []
    save_state_to_file(state)
    return state

def add_filename_to_list(state, list, directory, name):
    fullpath = get_fullpath(directory, name)
    if fullpath not in state[list]:
        state[list].append(fullpath)
        save_state_to_file(state)
    return state

def remove_filename_from_list(state, list, all=None, directory=None, name=None):
    if name:
        fullpath = get_fullpath(directory, name)
        if fullpath in state[list]:
            state[list].remove(fullpath)
    if all:
        state[list] = []
    save_state_to_file(state)
    return state


def set_videos_ids_file(state, videos_ids):
    try:
        directory = STATE_DIRECTORY
        name = "videos_ids_temp.xlsx"
        fullpath = export_list_to_excel(videos_ids, directory, name, ['videoId'])
        state["videos_ids_file"] = fullpath
        save_state_to_file(state)
    except:
        print("Error on set_videos_ids_file (state.py)")
        print(sys.exc_info()[0])
        traceback.print_exc()
    return state


def set_channels_ids_file(state, channels_ids):
    try:
        directory = STATE_DIRECTORY
        name = "channels_ids_temp.xlsx"
        fullpath = export_list_to_excel(channels_ids, directory, name, ['channelId'])
        state["channels_ids_file"] = fullpath
        save_state_to_file(state)
    except:
        print("Error on set_channels_ids_file (state.py)")
        print(sys.exc_info()[0])
        traceback.print_exc()
    return state


def set_videos_comments_count_file(state, comments_count):
    try:
        directory = STATE_DIRECTORY
        name = "videos_comments_count_temp.xlsx"
        #fullpath = export_dict_to_excel(comments_count,directory,name)
        abs_path = pathlib.Path().resolve()
        full_path = os.path.join(abs_path, directory)
        filename = secure_filename(name)
        filename_path = os.path.join(full_path, filename)
        df = pd.DataFrame(comments_count,index=[0])
        df.to_excel(filename_path)
        state[COMMENTS_COUNT_FILE] = filename_path
        save_state_to_file(state)
    except:
        print("Error on set_videos_ids_file (state.py)")
        print(sys.exc_info()[0])
        traceback.print_exc()
    return state


def set_video_index(state, value):
    state["video_index"] = value
    save_state_to_file(state)
    return state

def set_comment_index(state, value):
    state["comment_index"] = value
    save_state_to_file(state)
    return state

def set_channel_index(state, value):
    state["channel_index"] = value
    save_state_to_file(state)
    return state

#def set_pending(state, value):
#    state["pending"] = value
#    save_state_to_file(state)
#    return state

def under_quote_limit(state, cost=None):
    if not cost:
        cost = 0
    under = True
    if (state["quote_usage"] + cost)>(UNITS_QUOTE_LIMIT-SAFETY_BACKUP):
        under = False
    return under

def continue_to_retrieve(state):
    under = under_quote_limit(state, UNITS_PLAYLIST_LIST*2)
    return under

def set_all_retrieved(state, field, value):
    state[field] = value
    save_state_to_file(state)
    return state

def clear_state(state, clear_quote=False, clear_api_key=False):
    if clear_api_key:
        state["api_key"]= ""
    if clear_quote:
        state["quote_usage"] = 0
    state["actions"]= []
    state["videos_ids_file"]= ""
    state["channels_ids_file"] = ""
    state["videos_comments_count_file"] = None
    state["videos_files_to_merge"]= []
    state["videos_merged"] = ""
    state["comments_files_to_merge"]= []
    state["comments_merged"] = ""
    state["subcomments_files_to_merge"]=[]
    state["subcomments_merged"] = ""
    state["network_file"]= ""
    state["channels_files_to_merge"] = []
    state["channels_merged"] = ""
    state["video_index"]= 0
    state["comment_index"] = 0
    state["channel_index"] = 0
    state[ALL_VIDEOS_RETRIEVED] = False
    state[ALL_COMMENTS_RETRIEVED] = False
    state[ALL_CHANNELS_RETRIEVED] = False
    save_state_to_file(state)
    return state

def print_state(state):
    #print("api_key: "  + state["api_key"])
    print ("The information below is for debugging purposes: ******************")
    print("quote_usage: " + str(state["quote_usage"]))
    print("actions: ")
    print (state["actions"])
    print ("videos_ids_file: " + state["videos_ids_file"])
    print ("channels_ids_file: " + state["channels_ids_file"])
    comments_file = ""
    if state[COMMENTS_COUNT_FILE]:
        comments_file = state[COMMENTS_COUNT_FILE]
    print ("videos_comments_count_file: " + comments_file)
    print ("videos_files_to_merge: ")
    print (state["videos_files_to_merge"])
    print("videos_merged: ")
    if state["videos_merged"]:
        print (state["videos_merged"])
    print("comments_files_to_merge: ")
    print(state["comments_files_to_merge"])
    print ("comments_merged")
    if state["comments_merged"]:
        print (state["comments_merged"])
    print("subcomments_files_to_merge: ")
    print(state["subcomments_files_to_merge"])
    print ("subcomments_merged")
    print (state["subcomments_merged"])
    print ("channels_file_to_merge: ")
    print(state["channels_files_to_merge"])
    if state["channels_merged"]:
        print ("channels_merged: ")
        print (state["channels_merged"])
    print("network file: " + state["network_file"])
    print ("video index: " + str(state["video_index"]))
    print ("comment index: " + str(state["comment_index"]))
    print ("channel index: " + str(state["channel_index"]))
    print ("all videos retrieved:" + str(state[ALL_VIDEOS_RETRIEVED]))
    print ("all comments retrieved: " + str(state[ALL_COMMENTS_RETRIEVED]))
    print ("all channels retrieved: " + str(state[ALL_CHANNELS_RETRIEVED]))


def total_requests_cost(total_items, items_per_request, units_request):
    number_of_requests = math.ceil (total_items / items_per_request)
    total_cost = number_of_requests * units_request
    return total_cost


def number_of_items_with_quote(units_per_request, items_per_request):
    quote_available = (UNITS_QUOTE_LIMIT - state_yt[QUOTE_USAGE])
    number_of_requests = math.floor(quote_available / units_per_request)
    total_items = items_per_request * number_of_requests
    return total_items

def print_quote_usage():
    perc_usage = round((state_yt[QUOTE_USAGE]/UNITS_QUOTE_LIMIT) * 100,2)
    print ("\n** Quote Usage: {} units of {} units ({}%)\n".format(str(state_yt[QUOTE_USAGE]),UNITS_QUOTE_LIMIT,str(perc_usage)))


def get_videos_comments_count_file(videos_comments_count_filename):
    dict = read_excel_file_to_dict(videos_comments_count_filename)
    videos_comments_count = dict[0]
    return videos_comments_count






