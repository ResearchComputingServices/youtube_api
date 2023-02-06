import pprint
import traceback
import sys
from comments import get_video_comments
from utils import export_dict_to_excel
from utils import export_dict_to_csv
from utils import get_filename
from videos import create_video_metadata
from channels import get_videos_and_videocreators
from comments import get_videos_comments_and_commenters
from network import export_network_file
import pandas as pd
import state



#*****************************************************************************************************
#This function returns the title of the playlist given as argument
#*****************************************************************************************************
def get_playlist_title(youtube, playlistId):
    title = None
    request = youtube.playlists().list(
        id = playlistId,
        part='snippet'
    )
    response   = request.execute()
    state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_PLAYLIST_LIST)

    for item in response['items']:
        title = item["snippet"].get("title","playlist")

    return title


#*****************************************************************************************************
#This function retrieves the videos ids on a specific page from the API request
#(The API request provides "a page" of info at the time)
#*****************************************************************************************************
def get_playlist_videos_ids_on_page(youtube, playlist, nextPageToken, videos_ids):

    # List maxResults videos in a playlist
    requestVideosList = youtube.playlistItems().list(
        part='contentDetails,snippet',
        playlistId=playlist,
        maxResults=state.MAX_PLAYLISTITEMS_PER_REQUEST,  # max is 50
        pageToken=nextPageToken
    )
    responseVideosList = requestVideosList.execute()
    state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_PLAYLIST_ITEMS_LIST)

    # Obtain video_id for each video in the response
    for item in responseVideosList['items']:
        videoId = item['contentDetails']['videoId']
        if 'videoPublishedAt' in item['contentDetails']: #For some reason the API is bringing "ghost" videos in the playlist
            videos_ids.append(videoId)

    nextPageToken = responseVideosList.get('nextPageToken')

    return videos_ids, nextPageToken


#*****************************************************************************************************
#This function retrieves the videos ids for all the videos on the playlist given as argument
#*****************************************************************************************************
def get_playlist_videos_ids(youtube, playlist):
    nextPageToken = None
    pages = 0
    videos_ids = []
    while True:
        try:
            if state.under_quote_limit(state.state_yt, state.UNITS_PLAYLIST_ITEMS_LIST):
                videos_ids, nextPageToken = get_playlist_videos_ids_on_page(youtube, playlist, nextPageToken, videos_ids)
                pages = pages + 1
                if not nextPageToken:
                    break
            else:
                videos_ids = []
                break
        except:
            print("Error on getting video list for playlist ")
            print(sys.exc_info()[0])
            traceback.print_exc()

    return list(set(videos_ids))


#*****************************************************************************************************
#This function retrieves the metadata for a video and its creator (a channel) for all the videos
#in the playlist given as argument
#*****************************************************************************************************
def get_playlist_videos_and_videocreators(youtube, playlist, playlist_title, videos_ids=None):
    records={}
    try:
        if not videos_ids:
            videos_ids = get_playlist_videos_ids(youtube, playlist)
        if videos_ids:
            prefix_name = "playlist_" + playlist_title + "_videos_creators"
            records =  get_videos_and_videocreators(youtube, videos_ids, prefix_name)
    except:
        print("Error on getting video's metadata and creators for playlist ")
        print(sys.exc_info()[0])
        traceback.print_exc()
    return records


#*****************************************************************************************************
#This function retrieves the comments and replies for a video along the commenter metadata (a channel)
#for all the videos in the playlist given as argument
#*****************************************************************************************************
def get_playlist_videocomments_and_commenters(youtube, playlist, playlist_title, videos_ids=None):
    records={}
    try:
        if not videos_ids:
            videos_ids = get_playlist_videos_ids(youtube, playlist)
        prefix_name = "playlist_" + playlist_title + "_comments_commenters"
        records = get_videos_comments_and_commenters(youtube, videos_ids, prefix_name)
    except:
        print("Error on getting video comments for playlist ")
        print(sys.exc_info()[0])
        traceback.print_exc()
    return records



#*****************************************************************************************************
#This function calls the functions get_playlist_videos_and_videocreators and
#get_playlist_videocomments_and_commenters, calls the function export_network_file to combine the
#ouput records of those functions into a single excel file that will be the input to cytoscape.
#**************************************************************************************************`***
def get_playlist_network(youtube, playlist, playlist_title):
    print ("Retrieving videos' id from playlist \n")
    videos_ids = get_playlist_videos_ids(youtube, playlist)
    videos_ids = list(set(videos_ids))
    if videos_ids and len(videos_ids)>0:
        #Update state with all the actions: retrieve videos, retrieve comments and build network
        state.add_action(state.state_yt,state.ACTION_RETRIEVE_VIDEOS)
        state.add_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)
        state.add_action(state.state_yt, state.ACTION_CREATE_NETWORK)
        print ('Getting video and creators metadata \n')
        videos_records = get_playlist_videos_and_videocreators(youtube, playlist, playlist_title, videos_ids)
        print ('Getting comments and commenters metadata \n')
        comments_records = get_playlist_videocomments_and_commenters(youtube, playlist,playlist_title, videos_ids)
        print ('\nExporting network file \n')
        if videos_records and comments_records:
            if state.state_yt[state.ALL_VIDEOS_RETRIEVED] and state.state_yt[state.ALL_COMMENTS_RETRIEVED]:
                output_file = export_network_file(playlist_title, videos_records=videos_records, comments_records=comments_records)
                print("Output is in :" + output_file)


#*****************************************************************************************************
#This function retrieves the comments and replies for all the videos in the playlist given as argument
#*****************************************************************************************************`
def get_playlist_videos_comments(youtube, playlist, playlist_title):
    records = {}
    try:
        videos_ids = get_playlist_videos_ids(youtube, playlist)
        for video_id in videos_ids:
            print("***** Fetching comments for video " + video_id)
            records = get_video_comments(youtube, video_id, records)
    except:
        print("Error on getting video comments for playlist ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    print("\n")
    # Export info to excel
    directory = 'output'
    filename = get_filename('playlist_' + playlist_title + '_comments', 'xlsx')
    df = pd.DataFrame.from_dict(records, orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    filename = export_dict_to_excel(records, directory, filename)
    print('Output is in ' + filename)

    filename = get_filename('playlist_' + playlist_title + '_comments_only', 'csv')
    filename = export_dict_to_csv(sub_info, directory, filename)
    print('Output is in ' + filename)


#*****************************************************************************************************
#This function retrieves the video's metadata for all the videos in the playlist given as argument
#*****************************************************************************************************
def get_playlist_metadata(youtube, playlist, playlist_title):
    records = {}
    nextPageToken = None
    count = 1
    pages = 0

    while True:
        pages = pages + 1
        videos_ids = []
        videos_ids, nextPageToken = get_playlist_videos_ids_on_page(youtube, playlist, nextPageToken, videos_ids)
        # Request videos
        videos_request = youtube.videos().list(
            part="contentDetails,snippet,statistics",
            maxResults=state.MAX_VIDEOS_PER_REQUEST,
            id=','.join(videos_ids)
        )
        #Increase quote
        state.state_yt = state.update_quote_usage(state.state_yt,state.UNITS_VIDEOS_LIST)

        videos_response = videos_request.execute()
        for item in videos_response['items']:
            metadata = create_video_metadata(item)
            print('{} - Video {}'.format(count, metadata["videoId"]))
            #records[count] = metadata
            records[metadata["videoId"]] = metadata
            count = count + 1

        # if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    # Export info to excel
    directory = 'output'
    filename = get_filename('playlist_'+playlist_title + '_videos', 'xlsx')
    filename = export_dict_to_excel(records, directory, filename)
    print('Output: ' + filename)


