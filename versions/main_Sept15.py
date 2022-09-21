import json
import datetime
import pprint
import pandas as pd
from googleapiclient.discovery import build
from dateutil import parser
import io
import os
from googleapiclient.http import MediaIoBaseDownload

def get_api_key():
    with open('api_key.json') as client_secrets_file:
        client_secrets = json.load(client_secrets_file)
    if client_secrets:
        return client_secrets["key"]
    else:
        return None


def get_playlist():
    with open('config.json') as config_file:
        config_file = json.load(config_file)
    if config_file:
        pl = config_file["playlist"]
        index = pl.find("list=")
        if index:
            playlist = pl[index+5:]
            return playlist
    return None

def export_excel(dict):
    df = pd.DataFrame(dict).T
    #df.to_csv('info.csv')
    df.to_excel('info.xlsx')

def get_player_url(player):
    if player:
        index1 =player.find("src=")
        if index1:
            index2 = player.find('"',index1+7)
            if index2:
                url = player[index1+7:index2]
            return url
    return player

def convert_to_local_zone(datestring):
    try:
        #datestring = '2007-09-27T16:15:10Z'
        utc_dt = parser.parse(datestring)
        #print(utc_dt)
        local_dt = utc_dt.astimezone(None)
        #print (local_dt)
        date_time = local_dt.strftime("%Y-%m-%d, %H:%M:%S")
        #print("date and time:", date_time)
        return date_time
    except:
        return datestring


def get_english_caption(service, videoId, videoTitle):
    video_captions = service.captions().list(
        part="id,snippet",
        videoId=videoId
    )

    captions_response = video_captions.execute()
    print(captions_response)

    if captions_response:
        for item in captions_response["items"]:
            if item["snippet"]["language"]=='en':
                request = service.captions().download(
                    id=item['id']
                )
                # TODO: For this request to work, you must replace "YOUR_FILE"
                #       with the location where the downloaded content should be written.
                fh = io.FileIO(videoTitle+'.txt', "wb")

                download = MediaIoBaseDownload(fh, request)
                complete = False
                while not complete:
                    status, complete = download.next_chunk()
        return True
    return False


def get_info(api_key,playlist):

    # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
    youtube = build('youtube', 'v3', developerKey=api_key)

    records ={}
    nextPageToken = None
    count = 1
    while True:

        #count
        #print('-------------')
        #print(count)


        # List maxResults videos in a playlsit
        requestVideosList = youtube.playlistItems().list(
            part='contentDetails',
            playlistId=playlist,
            maxResults=5,
            pageToken=nextPageToken
        )
        responseVideosList = requestVideosList.execute()

        # Obtain video_id for each video in the response
        videos_ids = []
        for item in responseVideosList['items']:
            #print(item)
            #print('******')
            videoId = item['contentDetails']['videoId']
            #print(videoId)
            videos_ids.append(videoId)

        # Request all videos
        #print(','.join(videos_ids))
        videos_request = youtube.videos().list(
            part="contentDetails,player,snippet,statistics",
            id=','.join(videos_ids)
        )

        videos_response = videos_request.execute()

        now = datetime.datetime.now()
        current_datetime_str = now.strftime("%Y-%m-%d, %H:%M:%S")

        for item in videos_response['items']:
            #print ("Video Info:      \n ")
            #print(item)

            videoId = item["id"]
            print (videoId)
            url =  "https://youtu.be/" + videoId,
            print (url[0])
            metadata = {
                "videoId" : item["id"],
                "title": item["snippet"]["title"],
                "url": url[0],
                "publishedAt": convert_to_local_zone(item["snippet"]["publishedAt"]),
                "scrappedAt": current_datetime_str,
                "duration": item["contentDetails"]["duration"],
                #"player": get_player_url(item["player"]["embedHtml"]),
                #"caption": item["contentDetails"]["caption"],
                "views": item["statistics"]["viewCount"],
                "likes": item["statistics"]["likeCount"],
                "description": item["snippet"]["description"],
                "channelId": item["snippet"]["channelId"],
            }



            records[count] = metadata
            count = count + 1
            #print()

        #nextPageToken = responseVideosList.get('nextPageToken')
        nextPageToken = None

        if not nextPageToken:
            break;


    #print(records)
    #pprint.pprint(records)
    export_excel(records)









if __name__ == "__main__":
    api_key = get_api_key()
    playlist = get_playlist()

    #datestring = '2007-09-27T16:15:10Z'
    #utc_dt = parser.parse(datestring)
    #print(utc_dt)
    #central = utc_dt.astimezone(None)
    #print (central)
    #date_time = central.strftime("%Y-%m-%d, %H:%M:%S")
    #print("date and time:", date_time)

    #video_id ="6bACEX9x7U"
    #url_link = "https://youtu.be/" + video_id
    #print(url_link)

    if api_key:
        if playlist:
            get_info(api_key,playlist)
        else:
            print ("Verify format of YouTube playlist.")
    else:
        print ("YouTube API Key was not provided.")
