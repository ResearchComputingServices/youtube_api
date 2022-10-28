import pprint
import traceback
import sys
from utils import export_dict_to_excel
from utils import get_filename
from videos import create_video_snippet
from videos import create_video_metadata



def get_channel_activity(youtube, channel_id):

    record = {}
    try:
        requestActivities = youtube.activities().list(
            part="snippet,contentDetails",
            channelId=channel_id
        )
        responseActivities = requestActivities.execute()
        for item in responseActivities["items"]:
            if "snippet" in item:
                record["activityDate"] = item["snippet"].get("publishedAt","NA")
                record["activityType"] = item["snippet"].get("type","NA")
                actType = item["snippet"].get("title",None)
                if not actType:
                    actType = item["snippet"].get("channelTitle","NA")
                record["activityTitle"] = actType
            break
    except:
        print("Error on getting channels activity ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return record


def create_channel_dict(youtube, item):
    try:
        record ={}
        record["channelId"] = item["id"]
        if "snippet" in item:
            record["channel_title"] = item["snippet"].get("title","NA")
            record["channel_description"] = item["snippet"].get("description","NA")
            record["channel_url"] = "https://www.youtube.com/channel/" + item["id"]
            record["channel_JoinDate"] = item["snippet"].get("publishedAt","NA")
            record["channel_country"] = item["snippet"].get("country","NA")

        if "statistics" in item:
            record["channel_viewCount"] = item["statistics"].get("viewCount","NA")
            record["channel_subscriberCount"] = item["statistics"].get("subscriberCount","NA")
            record["channel_videoCount"] = item["statistics"].get("videoCount","NA")

        last_activity_date = get_channel_activity(youtube, item["id"])
        record.update(last_activity_date)
    except:
            print("Error on creating channel dictionary ")
            print(sys.exc_info()[0])
            traceback.print_exc()
    return record


def get_channel_videos_snippet(youtube, channel_id):

    records = {}
    nextPageToken = None
    count = 1
    pages = 1
    try:
        while True:
            video_channels_request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                maxResults=50,
                order="date",
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
            #if not nextPageToken or pages == 2:
            if not nextPageToken:
                break;

    except:
        print("Error on getting channels activity ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    # Export info to excel
    #export_dict_to_excel(records, 'snippet.xlsx')
    export_dict_to_excel(records, 'output', 'channel_' + channel_id + '_videos_metadata.xlsx')



def get_all_videos_by_a_channel_metadata(youtube, channel_id):

    records = {}
    nextPageToken = None
    count = 1
    pages = 1

    try:
        while True:
            video_channels_request = youtube.search().list(
                part="snippet",
                channelId=channel_id,
                type="video",
                maxResults=50,
                order="date",
                pageToken=nextPageToken

            )
            response_videos_channels= video_channels_request.execute()

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
                print('Video {}'.format(count))
                pprint.pprint(metadata)
                print('\n')
                records[count] = metadata
                count = count + 1

            nextPageToken = response_videos_channels.get('nextPageToken')
            pages = pages + 1
            #if not nextPageToken or pages == 2:
            if not nextPageToken:
                break;

    except:
        print("Error on getting channels activity ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    #Export info to excel
    filename = get_filename('channel_' + channel_id + '_videos', 'xlsx')
    export_dict_to_excel(records, 'output', filename)
    print("Output is in " + filename)
    return records



def get_channels_metadata(youtube, channel_ids, export):

    try:
        nextPageToken = None
        pages = 1
        count = 1

        while True:
            records = {}
            # Request all videos
            channels_request = youtube.channels().list(
                part="contentDetails,id,snippet,statistics,status,topicDetails",
                id=','.join(channel_ids),
                maxResults=50,
                pageToken=nextPageToken
            )

            channels_response = channels_request.execute()

            for item in channels_response["items"]:
                record = create_channel_dict(youtube, item)
                records[item["id"]] =record
                count = count +1


            nextPageToken = channels_response.get('nextPageToken')
            pages = pages + 1
            #if not nextPageToken or pages == 2:
            if not nextPageToken:
                break;
    except:
        print("Error on getting channel metadata for channels ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    if export==True:
        # Export info to excel
        filename = get_filename('channels_metadata','xlsx')
        export_dict_to_excel(records, 'output', filename)
        print ("Output is in " + filename)

    return records