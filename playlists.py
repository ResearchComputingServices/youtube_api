import pprint
import traceback
import sys
from comments import get_video_comments
from utils import export_dict_to_excel
from utils import export_dict_to_csv
from videos import create_video_metadata
from videos import create_video_and_channel_metadata
from channels import get_channels_metadata
from comments import get_video_comments_and_channels
import pandas as pd


def get_playlist_comments(youtube, playlist):

    records ={}
    nextPageToken = None
    pages = 0
    try:
        videos_ids = []
        while True:

            pages = pages + 1
            # List maxResults videos in a playlist
            requestVideosList = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist,
                maxResults=50,  #max is 50
                pageToken=nextPageToken
            )

            responseVideosList = requestVideosList.execute()

            # Obtain video_id for each video in the response
            for item in responseVideosList['items']:
                videoId = item['contentDetails']['videoId']
                videos_ids.append(videoId)
            nextPageToken = responseVideosList.get('nextPageToken')

            #if not nextPageToken or pages == 1:
            if not nextPageToken:
                break;


        count = 1
        for video_id in videos_ids:
            print ("\n ***** Fetching comments for video " + video_id + "\n")
            #To export all the comments for all the videos in the same excel file
            records = get_video_comments(youtube, video_id, records)


            #To export the comments of a video to a single file
            #records = get_video_comments(youtube, video_id)
            #if len(records)>0:
            #    name = video_id + '.xlsx'
            #    export_dict_to_excel(records, 'comments', name)
    except:
        print("Error on getting video comments for playlist ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    # Export info to excel
    df = pd.DataFrame.from_dict(records,orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    export_dict_to_excel(records, 'output', 'playlist_comments.xlsx')
    export_dict_to_csv(sub_info, 'output', 'playlist_sub_comments.csv')
    print ('Output is in playlist_comments.xlsx and playlist_sub_comments.csv')

def get_playlist_comments(youtube, playlist):

    records ={}
    nextPageToken = None
    pages = 0
    try:
        videos_ids = []
        while True:

            pages = pages + 1
            # List maxResults videos in a playlist
            requestVideosList = youtube.playlistItems().list(
                part='contentDetails',
                playlistId=playlist,
                maxResults=50,  #max is 50
                pageToken=nextPageToken
            )

            responseVideosList = requestVideosList.execute()

            # Obtain video_id for each video in the response
            for item in responseVideosList['items']:
                videoId = item['contentDetails']['videoId']
                videos_ids.append(videoId)
            nextPageToken = responseVideosList.get('nextPageToken')

            #if not nextPageToken or pages == 1:
            if not nextPageToken:
                break;


        count = 1
        for video_id in videos_ids:
            print ("\n ***** Fetching comments for video " + video_id + "\n")
            #To export all the comments for all the videos in the same excel file
            records = get_video_comments(youtube, video_id, records)


            #To export the comments of a video to a single file
            #records = get_video_comments(youtube, video_id)
            #if len(records)>0:
            #    name = video_id + '.xlsx'
            #    export_dict_to_excel(records, 'comments', name)
    except:
        print("Error on getting video comments for playlist ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    # Export info to excel
    df = pd.DataFrame.from_dict(records,orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    export_dict_to_excel(records, 'output', 'playlist_comments.xlsx')
    export_dict_to_csv(sub_info, 'output', 'playlist_sub_comments.csv')
    print ('\n')
    print('Output is in playlist_comments.xlsx')


def get_playlist_metadata(youtube, playlist):

    # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
    #youtube = build('youtube', 'v3', developerKey=api_key)

    records ={}
    nextPageToken = None
    count = 1
    pages = 0

    while True:

        pages = pages + 1
        # List maxResults videos in a playlist
        requestVideosList = youtube.playlistItems().list(
            part='contentDetails,snippet',
            playlistId=playlist,
            maxResults=50,  #Maximum 50
            pageToken=nextPageToken

        )
        responseVideosList = requestVideosList.execute()

        # Obtain video_id for each video in the response
        videos_ids = []
        for item in responseVideosList['items']:
            videoId = item['contentDetails']['videoId']
            videos_ids.append(videoId)

        #Request all videos
        videos_request = youtube.videos().list(
            part="contentDetails,snippet,statistics",
            id=','.join(videos_ids)
        )

        videos_response = videos_request.execute()


        for item in videos_response['items']:
            metadata = create_video_metadata(item)
            print ('Video {}'.format(count))
            pprint.pprint(metadata)
            print ('\n')

            records[count] = metadata
            count = count + 1


        nextPageToken = responseVideosList.get('nextPageToken')

        #if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    #Export info to excel
    #export_dict_to_excel(records, 'metadata.xlsx')
    export_dict_to_excel(records, 'output', 'playlist_metadata.xlsx')
    print ('Output is in playlist_metadata.xlsx')




def get_playlist_video_and_channels_metadata(youtube, playlist):

    # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
    #youtube = build('youtube', 'v3', developerKey=api_key)

    records ={}
    nextPageToken = None
    count = 1
    pages = 0

    while True:

        pages = pages + 1
        # List maxResults videos in a playlist
        requestVideosList = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist,
            maxResults=50,  #Maximum 50
            pageToken=nextPageToken

        )
        responseVideosList = requestVideosList.execute()

        # Obtain video_id for each video in the response
        videos_ids = []
        for item in responseVideosList['items']:
            videoId = item['contentDetails']['videoId']
            videos_ids.append(videoId)

        #Request all videos
        videos_request = youtube.videos().list(
            part="contentDetails,snippet,statistics",
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
            print ('Video {}'.format(count))
            pprint.pprint(metadata)
            print ('\n')

            records[count] = metadata
            count = count + 1


        nextPageToken = responseVideosList.get('nextPageToken')

        #if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    #Export info to excel
    #export_dict_to_excel(records, 'metadata.xlsx')
    export_dict_to_excel(records, 'output', 'playlist_videos_channels_metadata.xlsx')
    print ("The output is in playlist_videos_channels_metadata.xlsx")




def get_playlist_comments_and_channels_metadata(youtube, playlist):

    nextPageToken = None
    channel_records = {}
    records = {}
    pages = 0
    try:
        videos_ids = []
        while True:

            pages = pages + 1
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
                videos_ids.append(videoId)
            nextPageToken = responseVideosList.get('nextPageToken')

            #if not nextPageToken or pages == 2:
            if not nextPageToken:
                break;

        count = 1
        channelId_commenters = []
        for video_id in videos_ids:
            print("\n ***** Fetching comments for video " + video_id + "\n")
            # To export all the comments for all the videos in the same excel file
            records, channelId_commenters = get_video_comments_and_channels(youtube, video_id, records, channelId_commenters)

            # To export the comments of a video to a single file
            # records = get_video_comments(youtube, video_id)
            # if len(records)>0:
            #    name = video_id + '.xlsx'
            #    export_dict_to_excel(records, 'comments', name)

        #Get commenter's channels metadata
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

    # Export info to excel
    df = pd.DataFrame.from_dict(records, orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    export_dict_to_excel(records, 'output', 'playlist_comments_channels_metadata.xlsx')
    export_dict_to_csv(sub_info, 'output', 'playlist_sub_comments.csv')
    print ("\nThe output is in playlist_comments_channels_metadata.xlsx")