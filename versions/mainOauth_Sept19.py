from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import json
import datetime
import pprint
import pandas as pd
from googleapiclient.discovery import build
from dateutil import parser
import io
import os
import pickle
from googleapiclient.http import MediaIoBaseDownload
import pathlib
from youtube_transcript_api import YouTubeTranscriptApi




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


def write_transcript_to_file_2(transcript,video_title):

    try:
        filename = video_title + '_2.txt'
        with open(filename, 'w') as f:
            for item in transcript.items():
                start = item.get('start',0.0)
                duration = item.get('duration',0.0)
                text = item.get('text')

                line = "{},{} \n {}".format(str(start),str(start+duration),text)

                f.write('%s\n' % (line))
    except:
        print ("Error on writing transcript file for video: " + video_title)


def write_transcript_to_file(transcript,video_title):
    filename = video_title + '_2.txt'
    with open(filename, 'w') as f:
        for item in transcript:
            start = item.get('start',0.0)
            duration = item.get('duration',0.0)
            text = item.get('text')

            line = "{},{}\n{}\n".format(str(start),str(start+duration),text)

            f.write('%s\n' % (line))



def get_english_caption(service, videoId, videoTitle):

    try:
        video_captions = service.captions().list(
            part="id,snippet",
            videoId=videoId
        )

        caption = None
        downloaded = False
        captions_response = video_captions.execute()
        #print(captions_response)


        filename = videoTitle+'.txt'
        if captions_response:
            for item in captions_response["items"]:
                language = item["snippet"].get("language","NA")
                if 'en' in language.lower():
                    caption = True
                    request = service.captions().download(
                        id=item['id']
                    )
                    # TODO: For this request to work, you must replace "YOUR_FILE"
                    #       with the location where the downloaded content should be written.

                    fh = io.FileIO(filename, "wb")

                    download = MediaIoBaseDownload(fh, request)
                    complete = False
                    while not complete:
                        status, complete = download.next_chunk()
                    downloaded = True
    except:
        print ('Error when downloading transcript.')
        path = pathlib.Path().resolve()
        fullpath = os.path.join(path, filename)
        if os.path.exists(fullpath):
            os.remove(fullpath)
        print(fullpath)


    return caption, downloaded


def get_transcript_1(videoId):

    caption = False
    downloaded = False
    tr_type = ""
    tr = ''

    try:
        #Get transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)

        if transcript_list:

            caption = True
            downloaded = True

            transcript_manual = transcript_list.find_manually_created_transcript()
            for transcript in transcript_manual:
                if 'en' in transcript.language_code:
                    tr_type = "Manual"
                    tr = transcript.fetch()
                    return caption, tr_type, downloaded, tr

            transcript_generated = transcript_list.find_generated_transcript()
            for transcript in transcript_generated :
                if 'en' in transcript.language_code:
                    tr_type = "Generated"
                    tr = transcript.fetch()
                    return caption, tr_type, downloaded, tr


            for transcript in transcript_list:
                # translating the transcript will return another transcript object
                tr = transcript.translate('en').fetch()
                tr_type = "Translated from " +  transcript.language_code
                return caption, tr_type, downloaded, tr

    except:
        caption = False
        downloaded = False

    return caption, tr_type, downloaded, tr


def get_transcript_2(videoId):

    english_code_languages = ['en', 'en-AU', 'en-BZ', 'en-CA', 'en-IE', 'en-JM', 'en-NZ', 'en-ZA', 'en-TT', 'en-GB',
                              'en-US']
    caption = False
    downloaded = False
    tr_type = ""
    tr = ''

    # Get transcripts
    transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)

    if transcript_list:

        caption = True
        downloaded = True

        transcript_manual = transcript_list.find_manually_created_transcript(english_code_languages)
        for transcript in transcript_manual:
            if 'en' in transcript.language_code:
                tr_type = "Manual"
                tr = transcript.fetch()
                return caption, tr_type, downloaded, tr

        transcript_generated = transcript_list.find_generated_transcript(english_code_languages)
        for transcript in transcript_generated:
            if 'en' in transcript.language_code:
                tr_type = "Generated"
                tr = transcript.fetch()
                return caption, tr_type, downloaded, tr

        for transcript in transcript_list:
            # translating the transcript will return another transcript object
            tr = transcript.translate('en').fetch()
            tr_type = "Translated from " + transcript.language_code
            return caption, tr_type, downloaded, tr



    return caption, tr_type, downloaded, tr


def get_transcript(videoId):
    caption = False
    downloaded = False
    tr_type = ""
    tr = ''

    # Get transcripts
    transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)

    if transcript_list:

        caption = True
        downloaded = True

        try:
            #Priority to manual added transcript
            for transcript in transcript_list:
                if not transcript.is_generated:
                    if 'en' in transcript.language_code.lower():
                        tr_type = "Manual"
                        tr = transcript.fetch()
                        return caption, tr_type, downloaded, transcript.language_code, tr
        except:
            print ('Exception fetching manual transcript for video Id' + videoId)

        try:
            for transcript in transcript_list:
                if 'en' in transcript.language_code.lower():
                    tr_type = "Generated"
                    tr = transcript.fetch()
                    return caption, tr_type, downloaded, transcript.language_code, tr
        except:
            print('Exception fetching generated transcript for video Id' + videoId)

        try:
            for transcript in transcript_list:
                # translating the transcript will return another transcript object
                tr = transcript.translate('en').fetch()
                tr_type = "Translated from " + transcript.language_code
                return caption, tr_type, downloaded, transcript.language_code, tr
        except:
            print('Exception fetching translated transcript for video Id' + videoId)



    return caption, tr_type, downloaded, tr

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

    #caption, downloaded = get_english_caption(youtube, item["id"], item["snippet"].get("title", item["id"]))
    caption, tr_type, downloaded, language, tr = get_transcript(videoId)

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
        "English Transcript" : caption,
        "Transcript Type" : tr_type,
        "Downloaded Transcript" :downloaded,
        "Transcript Language" : language,
        "Transcript ": tr
    }

    write_transcript_to_file(tr, title)
    return metadata


def get_info(youtube,playlist):

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
            maxResults=1,
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
            #pprint.pprint(metadata)
            print ('\n')

            records[count] = metadata
            count = count + 1


        nextPageToken = responseVideosList.get('nextPageToken')

        if not nextPageToken or pages==1:
            break;

    #Export info to excel
    export_excel(records,'info.xlsx')


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



    #flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json",
    #                                                 scopes=["https://www.googleapis.com/auth/youtube.readonly",
    #                                                         "https://www.googleapis.com/auth/youtube.force-ssl",
    #                                                         "https://www.googleapis.com/auth/youtubepartner"])



    #print(credentials.to_json())
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube

if __name__ == "__main__":
    api_key = get_api_key()
    playlist = get_url_playlist()
    youtube = run_service()

    if youtube:
        if playlist:
            get_info(youtube,playlist)
        else:
            print ("Verify format of YouTube playlist.")
    else:
        print ("Error when creating service")


