import pprint
import traceback
import sys
from comments import get_video_comments
from utils import export_dict_to_excel
from utils import export_dict_to_csv
from utils import get_filename
from videos import create_video_metadata
from videos import create_video_and_channel_metadata
from channels import get_channels_metadata
from comments import get_video_comments_and_channels
from network import export_channels_videos_for_network
from network import export_comments_videos_for_network
import pandas as pd


def get_videos_ids_in_playlist_on_page(youtube, playlist, nextPageToken, videos_ids):

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


def get_videos_ids_in_playlist(youtube, playlist):
    nextPageToken = None
    pages = 0
    videos_ids = []
    while True:
        try:
            videos_ids, nextPageToken = get_videos_ids_in_playlist_on_page(youtube,playlist,nextPageToken,videos_ids)
            pages = pages + 1
            # if not nextPageToken or pages == 1:
            if not nextPageToken:
                break;
        except:
            print("Error on getting video list for playlist ")
            print(sys.exc_info()[0])
            traceback.print_exc()

    return videos_ids


def get_playlist_videos_comments(youtube, playlist):
    records ={}
    try:
        videos_ids = get_videos_ids_in_playlist(youtube, playlist)
        for video_id in videos_ids:
            print ("***** Fetching comments for video " + video_id)
            records = get_video_comments(youtube, video_id, records)
    except:
        print("Error on getting video comments for playlist ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    print("\n")
    # Export info to excel
    directory = 'output'
    filename = get_filename('playlist_comments', 'xlsx')
    df = pd.DataFrame.from_dict(records,orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    export_dict_to_excel(records, directory, filename)
    print ('Output is in ' + filename)

    filename = get_filename('playlist_sub_comments_', 'csv')
    export_dict_to_csv(sub_info, directory, filename)
    print('Output is in ' + filename)


def get_playlist_metadata(youtube, playlist):

    records ={}
    nextPageToken = None
    count = 1
    pages = 0

    while True:
        pages = pages + 1
        videos_ids = []
        videos_ids, nextPageToken = get_videos_ids_in_playlist_on_page(youtube, playlist, nextPageToken, videos_ids)
        #Request videos
        videos_request = youtube.videos().list(
            part="contentDetails,snippet,statistics",
            maxResults = 50,
            id=','.join(videos_ids)
        )

        videos_response = videos_request.execute()
        for item in videos_response['items']:
            metadata = create_video_metadata(item)
            print ('{} - Video {}'.format(count,metadata["videoId"]))
            records[count] = metadata
            count = count + 1

        #if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    #Export info to excel
    directory = 'output'
    filename = get_filename('playlist_metadata', 'xlsx')
    export_dict_to_excel(records, directory, filename)
    print ('Output: ' + filename)



def get_playlist_video_and_channels_metadata(youtube, playlist):

    # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
    #youtube = build('youtube', 'v3', developerKey=api_key)

    records ={}
    nextPageToken = None
    count = 1
    pages = 0

    while True:

        pages = pages + 1
        videos_ids=[]
        videos_ids, nextPageToken = get_videos_ids_in_playlist_on_page(youtube, playlist, nextPageToken, videos_ids)

        #Request all videos
        videos_request = youtube.videos().list(
            part="contentDetails,snippet,statistics",
            maxResults=50,
            id=','.join(videos_ids)
        )

        videos_response = videos_request.execute()

        #Get channel_id
        channels_ids = []
        for item in videos_response['items']:
            channelId = item["snippet"].get("channelId", None)
            channels_ids.append(channelId)

        channels_ids = set(channels_ids)
        channel_records = get_channels_metadata(youtube, channels_ids,False)

        for item in videos_response['items']:
            metadata = create_video_and_channel_metadata(item,channel_records)
            print ('{} - Video {}'.format(count,metadata["videoId"]))
            records[count] = metadata
            count = count + 1

        #if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    #Export info to excel


    directory = 'output'
    filename = get_filename('playlist_videos_channels', 'xlsx')
    export_dict_to_excel(records, directory, filename)
    print ("Output: " + filename)
    export_channels_videos_for_network(records)



def get_playlist_comments_and_channels_metadata(youtube, playlist):

    channel_records = {}
    records = {}
    try:
        videos_ids = get_videos_ids_in_playlist(youtube,playlist)
        channelId_commenters = []

        for video_id in videos_ids:
            print("***** Fetching comments for video " + video_id)
            records, channelId_commenters = get_video_comments_and_channels(youtube, video_id, records, channelId_commenters)


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
    filename = get_filename('playlist_comments_channels','xlsx')
    export_dict_to_excel(records, directory, filename)
    print("\nOutput: " + filename)

    filename = get_filename('playlist_sub_comments','csv')
    df = pd.DataFrame.from_dict(records, orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    export_dict_to_csv(sub_info, directory, filename)
    print ("\nOutput: "  +filename)

    export_comments_videos_for_network(records)



