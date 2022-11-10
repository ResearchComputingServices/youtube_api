import pprint
import traceback
import sys
from comments import get_video_comments
from utils import export_dict_to_excel
from utils import export_dict_to_csv
from utils import get_filename
from videos import create_video_metadata
from channels import create_video_and_creator_dict
from channels import get_videos_and_videocreators
from comments import get_single_video_comments_and_commenters
from comments import get_videos_comments_and_commenters
from network import export_network_file
from network import export_comments_videos_for_network
from channels import get_channels_metadata
import pandas as pd



#*****************************************************************************************************
#This function returns the title of the playlist given as argument
#*****************************************************************************************************
def get_playlist_title(youtube, playlistId):
    request = youtube.playlists().list(
        id = playlistId,
        part='snippet'
    )
    response   = request.execute()

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
        part='contentDetails',
        playlistId=playlist,
        maxResults=50,  # max is 50
        pageToken=nextPageToken
    )
    responseVideosList = requestVideosList.execute()

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
            videos_ids, nextPageToken = get_playlist_videos_ids_on_page(youtube, playlist, nextPageToken, videos_ids)
            pages = pages + 1
            # if not nextPageToken or pages == 1:
            if not nextPageToken:
                break;
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
        prefix_name = "playliyst_" + playlist_title + "_videos_creators"
        records = get_videos_and_videocreators(youtube, videos_ids, prefix_name)
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
    #videos_ids = videos_ids[1:57] ----> For testing and debugging only.
    if videos_ids and len(videos_ids)>0:
        print ('Getting video and creators metadata \n')
        videos_records = get_playlist_videos_and_videocreators(youtube, playlist, playlist_title, videos_ids)
        print ('Getting comments and commenters metadata \n')
        comments_records = get_playlist_videocomments_and_commenters(youtube, playlist,playlist_title, videos_ids)
        print ('\nExporting network file \n')
        output_file = export_network_file(playlist_title + "_", videos_records=videos_records, comments_records=comments_records)
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
            maxResults=50,
            id=','.join(videos_ids)
        )

        videos_response = videos_request.execute()
        for item in videos_response['items']:
            metadata = create_video_metadata(item)
            print('{} - Video {}'.format(count, metadata["videoId"]))
            records[count] = metadata
            count = count + 1

        # if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    # Export info to excel
    directory = 'output'
    filename = get_filename('playlist_'+playlist_title + '_videos', 'xlsx')
    filename = export_dict_to_excel(records, directory, filename)
    print('Output: ' + filename)



#*****************************************************************************************************
#To be deleted.
#*****************************************************************************************************
def get_playlist_videos_and_videocreators_old(youtube, playlist):
    # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
    # youtube = build('youtube', 'v3', developerKey=api_key)

    records = {}
    nextPageToken = None
    count = 1
    pages = 0

    while True:

        pages = pages + 1
        videos_ids = []
        videos_ids, nextPageToken = get_playlist_videos_ids_on_page(youtube, playlist, nextPageToken, videos_ids)

        # Request all videos
        videos_request = youtube.videos().list(
            part="contentDetails,snippet,statistics",
            maxResults=50,
            id=','.join(videos_ids)
        )

        videos_response = videos_request.execute()

        # Get channel_id
        channels_ids = []
        for item in videos_response['items']:
            channelId = item["snippet"].get("channelId", None)
            channels_ids.append(channelId)

        channels_ids = set(channels_ids)
        channel_records = get_channels_metadata(youtube, channels_ids, False)

        for item in videos_response['items']:
            metadata = create_video_and_creator_dict(item, channel_records)
            print('{} - Video {}'.format(count, metadata["videoId"]))
            records[count] = metadata
            count = count + 1

        # if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    # Export info to excel

    directory = 'output'
    filename = get_filename('playlist_videos_channels_old', 'xlsx')
    export_dict_to_excel(records, directory, filename)
    print("Output: " + filename)
    # export_channels_videos_for_network(records)
    return records



#*****************************************************************************************************
#To be deleted.
#*****************************************************************************************************
def get_playlist_comments_and_commenters_old(youtube, playlist):

    channel_records = {}
    records = {}
    try:
        videos_ids = get_playlist_videos_ids(youtube, playlist)
        channelId_commenters = []

        for video_id in videos_ids:
            print("***** Fetching comments for video " + video_id)
            records, channelId_commenters = get_single_video_comments_and_commenters(youtube, video_id, records, channelId_commenters)


        #Get commenter's channels metadata
        #We request at most 50 channels at the time to avoid breaking the API
        channelId_commenters = list(set(channelId_commenters))
        slice = True
        start = 0
        while (slice):
            end = start + 50
            if end > len(channelId_commenters):
                end=len(channelId_commenters)
                slice = False
            r = get_channels_metadata(youtube, channelId_commenters[start:end], False)
            channel_records.update(r)
            start = end

        if len(records)>0:
            for key, item in records.items():
                try:
                    channel_id_commenter = item["authorChannelId"]
                    channel_info = channel_records[channel_id_commenter]
                    item.update(channel_info)
                except:
                    print ('Error on: ' + channel_id_commenter)
    except:
        print("Error on getting video comments for playlist ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    print("\n")
    # Export info to excel
    directory = 'output'
    filename = get_filename('playlist_comments_channels_old','xlsx')
    export_dict_to_excel(records, directory, filename)
    print("\nOutput: " + filename)

    filename = get_filename('playlist_sub_comments','csv')
    df = pd.DataFrame.from_dict(records, orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    export_dict_to_csv(sub_info, directory, filename)
    print ("\nOutput: "  +filename)

    export_comments_videos_for_network(records)
    return records

