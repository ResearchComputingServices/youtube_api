import pprint
import traceback
import sys
from videos import create_video_metadata
from videos import create_video_snippet
from utils import export_dict_to_excel
from utils import get_filename


def get_videos_by_keyword_snippet(youtube, query):

    records = {}
    nextPageToken = None

    count = 1
    pages = 0

    try:
        while True:
            video_channels_request = youtube.search().list(
                part="snippet",
                q = query,
                type="video",
                maxResults=50,
                order="relevance",
                pageToken=nextPageToken

            )
            response_videos_channels= video_channels_request.execute()

            for item in response_videos_channels['items']:
                metadata = create_video_snippet(item)
                print('Video {}'.format(count))
                pprint.pprint(metadata)
                print('\n')

                records[count] = metadata
                count = count + 1

            nextPageToken = response_videos_channels.get('nextPageToken')
            pages = pages + 1

            if not nextPageToken or pages == 1:
            #if not nextPageToken:
                break;

    except:
        print("Error on getting channels activity ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    # Export info to excel
    #export_dict_to_excel(records, 'queries_videos.xlsx')
    export_dict_to_excel(records, 'output', + 'query_metadata.xlsx')


def get_videos_by_keyword_metadata(youtube, query):
    records = {}
    nextPageToken = None
    count = 1
    pages = 1

    try:
        while True:
            video_channels_request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=50,
                order="relevance",
                pageToken=nextPageToken

            )
            response_videos_channels = video_channels_request.execute()

            # Obtain video_id for each video in the response
            videos_ids = []
            for item in response_videos_channels['items']:
                videoId = item["id"].get("videoId", "N/A")
                videos_ids.append(videoId)

            # Request all videos
            videos_request = youtube.videos().list(
                part="contentDetails,snippet,statistics",
                id=','.join(videos_ids)
            )

            videos_response = videos_request.execute()

            for item in videos_response['items']:
                metadata = create_video_metadata(item)
                print('{} - Video {}'.format(count, item["id"]))
                records[count] = metadata
                count = count + 1

            nextPageToken = response_videos_channels.get('nextPageToken')
            pages = pages + 1
            if not nextPageToken or pages == 3:
                # if not nextPageToken:
                break;

    except:
        print("Error on getting channels activity ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    # Export info to excel
    #export_dict_to_excel(records, 'queries_videos.xlsx')
    filename = get_filename('videos_query_metadata','xlsx')
    export_dict_to_excel(records, 'output', filename)
    print ("Output is in: " + filename)



