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

def export_excel(dict,filename):
    df = pd.DataFrame(dict).T
    df.to_excel(filename)

def convert_to_local_zone(datestring):
    try:
        utc_dt = parser.parse(datestring)
        local_dt = utc_dt.astimezone(None)
        date_time = local_dt.strftime("%Y-%m-%d, %H:%M:%S")
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

def create_dict(item):

    now = datetime.datetime.now()
    current_datetime_str = now.strftime("%Y-%m-%d, %H:%M:%S")

    videoId =   item.get("id","N/A")

    title = ""
    if "snippet" in item:
        title = item["snippet"].get("title", "N/A")
        publishedDate = convert_to_local_zone(item["snippet"].get("publishedAt", None))
        description = item["snippet"].get("description", "N/A")
        channelId = item["snippet"].get("channelId", "N/A")


    url = "https://youtu.be/" + videoId

    if "statistics" in item:
        views =  item["statistics"].get("viewCount", "N/A")
        likes = item["statistics"].get("likeCount","N/A")
        favoriteCount = item["statistics"].get("favoriteCount","N/A")
        commentsCount = item["statistics"].get("commentCount","N/A")

    if "contentDetails" in item:
        duration = item["contentDetails"].get("duration", "N/A")

    metadata = {
        "videoId": videoId,
        "title": title,
        "url": url,
        "publishedAt": publishedDate,
        "scrappedAt": current_datetime_str,
        "duration": duration,
        "views":  views,
        "likes": likes,
        "favoriteCount":  favoriteCount,
        "commentsCount": commentsCount,
        "description":  description,
        "channelId":  channelId
    }
    return metadata


def get_info(api_key,playlist):

    # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
    youtube = build('youtube', 'v3', developerKey=api_key)

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
            maxResults=5,
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
            metadata = create_dict(item)

            print ('Video {}'.format(count))
            pprint.pprint(metadata)
            print ('\n')

            records[count] = metadata
            count = count + 1


        nextPageToken = responseVideosList.get('nextPageToken')

        if not nextPageToken or pages==2:
            break;

    #Export info to excel
    export_excel(records,'info.xlsx')




if __name__ == "__main__":
    api_key = get_api_key()
    playlist = get_url_playlist()



    if api_key:
        if playlist:
            get_info(api_key,playlist)
        else:
            print ("Verify format of YouTube playlist.")
    else:
        print ("YouTube API Key was not provided.")
