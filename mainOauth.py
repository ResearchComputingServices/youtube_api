from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import datetime
import pprint
import pandas as pd
from googleapiclient.discovery import build
from dateutil import parser
#import io
import os
import pickle
#from googleapiclient.http import MediaIoBaseDownload
import pathlib
import traceback
import sys
from youtube_transcript_api import YouTubeTranscriptApi
from werkzeug.utils import secure_filename




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


def export_dict_to_excel(dict, filename):
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

def write_transcript_to_file(transcript,video_title,video_id):
    try:

        directory = 'transcripts'
        abs_path = pathlib.Path().resolve()
        full_path = os.path.join(abs_path, directory)
        name = video_title + '_' + video_id + '.txt'
        filename = secure_filename(name)
        file_path = os.path.join(full_path, filename)

        with open(file_path, 'w') as f:
            for item in transcript:
                start = item.get('start',0.0)
                duration = item.get('duration',0.0)
                text = item.get('text')
                line = "{},{}\n{}\n".format(str(start),str(start+duration),text)
                f.write('%s\n' % (line))
    except:
        print("Error on writing transcript file for video: " + video_title)
        print(sys.exc_info()[0])
        traceback.print_exc()
        if os.path.exists(file_path):
            os.remove(file_path)
        file_path = ''

    return file_path


def get_video_transcript(videoId):

    transcript_data={}


    try:
        # Get transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)
        if transcript_list:
            # Priority to manual added transcript
            for transcript in transcript_list:
                if not transcript.is_generated:
                    if 'en' in transcript.language_code.lower():
                        transcript_data["tr_type"] = "Manual"
                        transcript_data["language"] = transcript.language_code
                        transcript_data["data"] = transcript.fetch()
                        return transcript_data

            # Then automatically generated
            for transcript in transcript_list:
                if 'en' in transcript.language_code.lower():
                    transcript_data["tr_type"] = "Generated"
                    transcript_data["language"] = transcript.language_code
                    transcript_data["data"] = transcript.fetch()
                    return transcript_data

            # Translated
            for transcript in transcript_list:
                # translating the transcript will return another transcript object
                transcript_data["tr_type"] = "Translated from " + transcript.language_code
                transcript_data["language"] = "English"
                transcript_data["data"] = transcript.translate('en').fetch()
                return transcript_data
    except:
        print ('No transcript available.')

    transcript_data["tr_type"] = ""
    transcript_data["language"] = ""
    transcript_data["data"] = ""

    return transcript_data


def create_dict(item):

    try:
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

        transcript_dict = get_video_transcript(videoId)
        transcript_filename=''
        if transcript_dict['data']:
            transcript_filename = write_transcript_to_file(transcript_dict["data"], title, videoId)

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
            "channelId":  channelId,
            "Transcript Language": transcript_dict["language"],
            "Transcript Type" : transcript_dict["tr_type"],
            "Downloaded Transcript" : transcript_filename
        }
    except:
        print("Error on creating dict: \n")
        print(item)
        print("\n")
        print(sys.exc_info()[0])
        traceback.print_exc()
        metadata = {
            "videoId": "",
            "title": "",
            "url": "",
            "publishedAt": "",
            "scrappedAt": "",
            "duration": "",
            "views": "",
            "likes": "",
            "favoriteCount": "",
            "commentsCount": "",
            "description": "",
            "channelId": "",
            "Transcript Language": "",
            "Transcript Type": "",
            "Downloaded Transcript": ""
        }

    return metadata


def get_playlist_info(youtube, playlist):

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

        #if not nextPageToken or pages == 1:
        if not nextPageToken:
            break;

    #Export info to excel
    export_dict_to_excel(records, 'info.xlsx')



def get_video_info(youtube, video_id):

    records ={}

    #Request the video
    videos_request = youtube.videos().list(
        part="contentDetails,snippet,statistics",
        id=video_id
    )

    videos_response = videos_request.execute()

    for item in videos_response['items']:
        metadata = create_dict(item)
        pprint.pprint(metadata)
        print ('\n')

        records[1] = metadata

    #Export info to excel
    export_dict_to_excel(records, 'info.xlsx')



def run_service():

    credentials = None
    # token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            credentials.refresh(Request())
        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly',
                    'https://www.googleapis.com/auth/youtube.force-ssl'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)



    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

if __name__ == "__main__":
    api_key = get_api_key()
    playlist = get_url_playlist()
    youtube = run_service()

    #video_id = '1aBWct8VBXE'
    #get_video_info(youtube, video_id)

    if youtube:
        if playlist:
            get_playlist_info(youtube, playlist)
        else:
            print ("Verify format of YouTube playlist.")
    else:
        print ("Error when creating service")


