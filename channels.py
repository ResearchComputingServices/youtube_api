import pprint
import traceback
import sys
import datetime
from utils import export_dict_to_excel
from utils import get_filename
from utils import read_excel_file_to_data_frame
from utils import convert_to_local_zone
from videos import create_video_metadata
from videos import get_video_transcript
from videos import write_transcript_to_file


#*****************************************************************************************************
#This function gets the most recent activity of a channel along with the type of activity
#*****************************************************************************************************
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

#*****************************************************************************************************
#This function creates a dictionary with a channel's metadata (send it as parameter).
#This dictionary will be used to create a record on the output excel file
#*****************************************************************************************************
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

        #last_activity_date = get_channel_activity(youtube, item["id"])
        #record.update(last_activity_date)
    except:
            print("Error on creating channel dictionary ")
            print(sys.exc_info()[0])
            traceback.print_exc()
    return record





#*****************************************************************************************************
#This function creates a dictionary that combines a video's and its creator (a channel) metadata
#The video's metadata is sent in the parameter item
#The information of the channel is located in channel_records which is a dictionary of channel's metadata
#This dictionary will be used to create a record on the output excel file
#*****************************************************************************************************
def create_video_and_creator_dict(item, channels_records):

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

        channel_info = None
        if channels_records:
            try:
                channel_info = channels_records[channelId]
            except:
                channel_info = None

        metadata = {
            "videoId": videoId,
            "video_title": title,
            "video_url": url,
            "video_publishedAt": publishedDate,
            "video_scrappedAt": current_datetime_str,
            "video_duration": duration,
            "video_views":  views,
            "video_likes": likes,
            "video_favoriteCount":  favoriteCount,
            "video_commentsCount": commentsCount,
            "video_description":  description,
            "video_Transcript Language": transcript_dict["language"],
            "video_Transcript Type" : transcript_dict["tr_type"],
            "video_Downloaded Transcript" : transcript_filename,
            "video_channelId": channelId
        }
        metadata.update(channel_info)
    except:
        print("Error on creating dict: \n")
        print(item)
        print("\n")
        print(sys.exc_info()[0])
        traceback.print_exc()
        metadata = {
            "videoId": "",
            "video_title": "",
            "video_url": "",
            "video_publishedAt": "",
            "video_scrappedAt": "",
            "video_duration": "",
            "video_views": "",
            "video_likes": "",
            "video_favoriteCount": "",
            "video_commentsCount": "",
            "video_description": "",
            "video_channelId": "",
            "video_Transcript Language": "",
            "video_Transcript Type": "",
            "video_Downloaded Transcript": ""
        }

    return metadata



#*****************************************************************************************************
#This function finds all the videos created by channel_id and return the metadata for these videos
#as a dictionary of dictionaries
#*****************************************************************************************************
def get_all_videos_by_a_channel(youtube, channel_id):

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
                #pprint.pprint(metadata)
                print('\n')
                records[count] = metadata
                count = count + 1

            nextPageToken = response_videos_channels.get('nextPageToken')
            pages = pages + 1
            #if not nextPageToken or pages == 2:
            if not nextPageToken:
                break;

    except:
        print("Error on getting all videos by a channel ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    #Export info to excel
    filename = get_filename('channel_' + channel_id + '_videos', 'xlsx')
    export_dict_to_excel(records, 'output', filename)
    print("Output is in " + filename)
    return records



#*****************************************************************************************************
#This function retrieves the channels' metadata for each channel in channel_ids
#The metadata is returned as a dictionary of dictionaries
#*****************************************************************************************************
def get_channels_metadata(youtube, channel_ids, export):

    try:
        nextPageToken = None
        while True:
            records = {}
            # Request all channels
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

            nextPageToken = channels_response.get('nextPageToken')
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



#*****************************************************************************************************
#For a given list of videos ids (videos_ids), this function retrieves the metadata for each video and
#its creator.
#It returns a dictionary where each entry is a dictionary combining both metadata
#The functio also exports to excel the combined metadata
#*****************************************************************************************************
def get_videos_and_videocreators(youtube, videos_ids, prefix_name):
    records = {}
    count = 1
    # We request at most 50 videos at the time to avoid breaking the API
    slicing = True
    start = 0

    original_videos_ids = videos_ids
    while (slicing):
        end = start + 50
        if end >= len(original_videos_ids):
            end = len(original_videos_ids)
            slicing = False

        videos_ids = original_videos_ids[start:end]
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

        #Merge video and channel info in only one dictionary
        for item in videos_response['items']:
            metadata = create_video_and_creator_dict(item, channel_records)
            print('{} - Video {}'.format(count, metadata["videoId"]))
            records[count] = metadata
            count = count + 1

        start = end

    # Export info to excel
    directory = 'output'
    filename = get_filename(prefix_name, 'xlsx')
    filename = export_dict_to_excel(records, directory, filename)
    print("Output: " + filename)
    # export_channels_videos_for_network(records)
    return records

#*****************************************************************************************************
#This function extracts a list of videos ids from an excel file (The excel file must contain the column
# videoId with the videos' ids)
#Once extracted this list, the function then calls the function get_videos_and_videocreators to retrieve
#the videos and its creators' metadata.
#*****************************************************************************************************

def get_videos_and_videocreators_from_file(youtube, filename, prefix):
    try:
        #Load file
        df, success = read_excel_file_to_data_frame(filename,['videoId'])
        if success:
            #Convert to list
            dfT = df.T
            videos_ids = dfT.values.tolist()
            prefix_name = "file_"+ prefix + "_videos_creators"
            #Get data from YouTube API
            get_videos_and_videocreators(youtube, videos_ids[0], prefix_name)
    except:
        print("Error on get_videos_comments_and_commenters_from_file")
        print(sys.exc_info()[0])
        traceback.print_exc()









