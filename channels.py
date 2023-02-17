import traceback
import sys
import datetime
import state
from utils import export_dict_to_excel
from utils import get_filename
from utils import preprocess_string
from utils import convert_to_local_zone
from utils import get_ids_from_file
from videos import create_video_metadata
from videos import get_video_transcript
from videos import write_transcript_to_file
from utils import get_filename_ordered



#*****************************************************************************************************
#This function gets the most recent activity of a channel along with the type of activity
#*****************************************************************************************************
def get_channel_activity(youtube, channel_id):

    record = {}
    try:
        if state.under_quote_limit(state.state_yt, state.UNITS_ACTIVITIES_LIST):
            requestActivities = youtube.activities().list(
                part="snippet,contentDetails",
                channelId=channel_id
            )
            state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_ACTIVITIES_LIST)
            responseActivities = requestActivities.execute()

            if len(responseActivities["items"])>0:
                for item in responseActivities["items"]:
                    if "snippet" in item:
                        record["activityDate"] = item["snippet"].get("publishedAt","NA")
                        record["activityType"] = item["snippet"].get("type","NA")
                        actType = item["snippet"].get("title",None)
                        if not actType:
                            actType = item["snippet"].get("channelTitle","NA")
                        record["activityTitle"] = preprocess_string(actType)
                    break
            else:
                record=-1
        else:
            record = -2
            return record
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
            record["channel_title"] = preprocess_string(item["snippet"].get("title","NA"))
            record["channel_description"] = preprocess_string(item["snippet"].get("description","NA"))
            record["channel_url"] = "www.youtube.com/channel/" + item["id"]
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
            title = preprocess_string(item["snippet"].get("title", "N/A"))
            publishedDate = convert_to_local_zone(item["snippet"].get("publishedAt", None))
            description = preprocess_string(item["snippet"].get("description", "N/A"))
            channelId = item["snippet"].get("channelId", "N/A")


        url = "youtu.be/" + videoId

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
            if state.under_quote_limit(state.state_yt, state.UNITS_SEARCH_LIST+state.UNITS_VIDEOS_LIST):
                video_channels_request = youtube.search().list(
                    part="snippet",
                    channelId=channel_id,
                    type="video",
                    maxResults=state.MAX_SEARCH_RESULTS_PER_REQUEST,
                    order="date",
                    pageToken=nextPageToken

                )
                state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_SEARCH_LIST)
                response_videos_channels= video_channels_request.execute()

                # Obtain video_id for each video in the response
                videos_ids = []
                #There is at least one video to register
                if len(response_videos_channels['items'])>0:
                    for item in response_videos_channels['items']:
                        videoId = item["id"].get("videoId", "N/A")
                        videos_ids.append(videoId)

                    # Request all videos
                    videos_request = youtube.videos().list(
                        part="contentDetails,snippet,statistics",
                        id=','.join(videos_ids)
                    )
                    state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_VIDEOS_LIST)
                    videos_response = videos_request.execute()

                    for item in videos_response['items']:
                        metadata = create_video_metadata(item)
                        print('Channel {} - Video {} {}'.format(channel_id,item["id"],count))
                        #pprint.pprint(metadata)
                        records[count] = metadata
                        count = count + 1
                else:
                    records = -1
                nextPageToken = response_videos_channels.get('nextPageToken')
                pages = pages + 1
                if not nextPageToken:
                    break;
            else:
                records = -2
                return records

    except:
        print("Error on getting all videos by a channel ")
        print(sys.exc_info()[0])
        traceback.print_exc()
        return None

    return records



#*****************************************************************************************************
#This function retrieves the channels' metadata for each channel in channel_ids
#The metadata is returned as a dictionary of dictionaries
#*****************************************************************************************************
def get_channels_metadata(youtube, channel_ids, export):

    try:

        if len(channel_ids)==0:
                return {}

        nextPageToken = None
        while True:
            records = {}
            # Request all channels
            channels_request = youtube.channels().list(
                part="contentDetails,id,snippet,statistics,status,topicDetails",
                id=','.join(channel_ids),
                maxResults=state.MAX_CHANNELS_PER_REQUEST,
                pageToken=nextPageToken
            )

            # Update quote usage
            state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_CHANNELS_LIST)
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
def get_videos_and_videocreators(youtube, videos_ids, prefix_name, start_index=None):

    records = {}
    count = 1
    # We request at most 50 videos at the time to avoid breaking the API
    slicing = True

    if start_index:
        start  = start_index
    else:
        start = 0

    original_videos_ids = videos_ids

    retrieving_cost = state.total_requests_cost(len(videos_ids)-start,state.MAX_VIDEOS_PER_REQUEST,state.UNITS_VIDEOS_LIST)
    print ("Retrieving {} videos' metadata with a total cost of {} units".format(len(videos_ids)-start,retrieving_cost))
    #Add action to state
    state.state_yt = state.add_action(state.state_yt, state.ACTION_RETRIEVE_VIDEOS)
    state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_VIDEOS_RETRIEVED, False)

    #Save videos_ids to be processed after if we run out of quote
    state.state_yt = state.set_videos_ids_file(state.state_yt,videos_ids)
    #Add index of the first video to be processed
    state.state_yt = state.set_video_index(state.state_yt, start)
    end=start
    try:
        while (slicing):
            #The cost of retrieving videos and channels
            retrieving_cost = state.UNITS_VIDEOS_LIST + state.UNITS_CHANNELS_LIST

            #Check if there is available quote
            if state.under_quote_limit(state.state_yt, retrieving_cost):
                end = start + state.MAX_VIDEOS_PER_REQUEST
                if end >= len(original_videos_ids):
                    end = len(original_videos_ids)
                    slicing = False

                videos_ids = original_videos_ids[start:end]
                # Request all videos
                videos_request = youtube.videos().list(
                    part="contentDetails,snippet,statistics",
                    maxResults=state.MAX_VIDEOS_PER_REQUEST,
                    id=','.join(videos_ids)
                )
                # Update quote_usage
                state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_VIDEOS_LIST)
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
                    #records[count] = metadata
                    records[metadata["videoId"]]=metadata
                    count = count + 1

                start = end
                # Add index of the first video to be processed
                state.state_yt = state.set_video_index(state.state_yt, start)
            else:
                slicing = False
    except:
        print("Error on get_videos_and_videocreators")
        print(sys.exc_info()[0])
        traceback.print_exc()

    # Export info to excel
    if len(records)>0:
        directory = 'output'
        filename = get_filename_ordered(directory, prefix_name, 'xlsx')
        filename_path = export_dict_to_excel(records, directory, filename)
        print("Output: " + filename_path)

        #Add output filename to the list of files to merge (in case the action was not completed)
        state.add_filename_to_list(state.state_yt, state.LIST_VIDEOS_TO_MERGE, directory, filename)

    #if state.under_quote_limit(state.state_yt):
    #All videos have been retrieved
    if end >= len(original_videos_ids):
        #All the retrieval was completed sucessfully
        state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_VIDEOS)
        state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_VIDEOS_RETRIEVED, True)

    # export_channels_videos_for_network(records)
    return records


#-----------------------------------------------------------------------------------------------------------------------
#This function extracts a list of videos ids from an excel file (The excel file must contain the column
#videoId with the videos' ids)
#Once extracted this list, the function then calls the function get_videos_and_videocreators to retrieve
#the videos and its creators' metadata.
#-----------------------------------------------------------------------------------------------------------------------
def get_videos_and_videocreators_from_file(youtube, filename, prefix, start_index=None):
    try:
        #Load file
        videos_ids = get_ids_from_file(filename, "videoId")
        if videos_ids:
            prefix_name = "file_"+ prefix + "_videos_creators"
            #Get data from YouTube API
            get_videos_and_videocreators(youtube, videos_ids, prefix_name, start_index)
        else:
            print ("Video's ids couldn't be retrieved. Check input file.")
    except:
        print("Error on get_videos_and_videocreators_from_file")
        print(sys.exc_info()[0])
        traceback.print_exc()






#***********************************************************************************************************************
#Get last activity for a list of channels
#***********************************************************************************************************************
def get_channels_activity_from_file(youtube, filename, prefix, start_index=None):
    try:
        #Load file
        records={}
        print ("Retrieving the last activity of all the channels... \n")
        channels_ids_ori = get_ids_from_file(filename, "channelId")
        channels_ids = remove_duplicates(channels_ids_ori)

        if channels_ids:
            state.state_yt = state.add_action(state.state_yt,  state.ACTION_RETRIEVE_CHANNELS_ACTIVITY)
            state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_CHANNELS_RETRIEVED, False)

            # Add index of the first channel to be processed
            if not start_index:
                start_index = 0

            state.state_yt = state.set_channel_index(state.state_yt, start_index)

            # Save channels_ids to be processed after if we run out of quote
            state.state_yt = state.set_channels_ids_file(state.state_yt, channels_ids)

            # Get data from YouTube API
            # Get data from YouTube API
            while (state.under_quote_limit(state.state_yt, state.UNITS_ACTIVITIES_LIST)) and (
                    start_index < len(channels_ids)):
                id = channels_ids[start_index]
                print ("Processing channel {}".format(id))
                r = get_channel_activity(youtube, id)

                #Run out of quote
                if r and r==-2:
                    break

                if r and r!=-1:
                    records[id] = r

                start_index = start_index + 1
                state.state_yt = state.set_channel_index(state.state_yt, start_index)

            if len(records) > 0:
                # Export info to excel
                directory = 'output'
                filename = get_filename_ordered(directory, prefix + "channels_activity", 'xlsx')
                filename_path = export_dict_to_excel(records, directory, filename)
                print("Output: " + filename_path)

                # Add output filename to the list of files to merge (in case the action was not completed)
                state.add_filename_to_list(state.state_yt, state.LIST_CHANNELS_TO_MERGE, directory, filename)

            # All videos have been retrieved
            if start_index >= len(channels_ids):
                # All the retrieval were completed successfully
                state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_CHANNELS_ACTIVITY)
                state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_CHANNELS_RETRIEVED, True)
            else:
                print("\nOut of quote. Not all the channels were processed. \n")
        else:
            print ("Channel's ids couldn't be retrieved. Check input file.")
    except:
        print("Error on get_channels_activity_from_file")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return


#***********************************************************************************************************************
#Get all videos for all the channels ids in a file
#***********************************************************************************************************************
def get_all_videos_by_all_channels_from_file(youtube, filename, prefix, start_index = None):
    #Load file
    try:
        records={}
        count=0
        channels_ids_ori = get_ids_from_file(filename, "channelId")
        channels_ids = remove_duplicates(channels_ids_ori)
        if channels_ids:
            print ("Retrieving all videos for all the channels in a given file...")
            state.state_yt = state.add_action(state.state_yt, state.ACTION_RETRIEVE_CHANNELS_ALL_VIDEOS)
            state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_CHANNELS_RETRIEVED, False)

            # Add index of the first channel to be processed
            if not start_index:
                start_index = 0

            state.state_yt = state.set_channel_index(state.state_yt, start_index)

            # Save channels_ids to be processed after if we run out of quote
            state.state_yt = state.set_channels_ids_file(state.state_yt, channels_ids)

            #Get data from YouTube API
            # Get data from YouTube API
            maximum_retrieving_cost = state.UNITS_SEARCH_LIST*5+state.UNITS_VIDEOS_LIST*5
            while (state.under_quote_limit(state.state_yt, maximum_retrieving_cost) and (start_index < len(channels_ids))):
                id = channels_ids[start_index]
                videos = get_all_videos_by_a_channel(youtube, id)
                if videos and videos==-2: #We run out of quote
                    break
                if videos and videos!=-1: #The channel doesn't have any updated videos
                    for video in videos.items():
                        video[1]["channelId"] = id
                        records[count] = video[1]
                        count = count + 1
                else:
                    print ("Channel {} doesn't have uploaded videos.".format(id))
                start_index = start_index + 1
                state.state_yt = state.set_channel_index(state.state_yt, start_index)

            if len(records) > 0:
                #Export info to excel
                directory = 'output'
                filename = get_filename_ordered(directory, prefix + "all_videos_by_channels", 'xlsx')
                filename_path = export_dict_to_excel(records, directory, filename)
                print("Output: " + filename_path)

                # Add output filename to the list of files to merge (in case the action was not completed)
                state.add_filename_to_list(state.state_yt, state.LIST_CHANNELS_TO_MERGE, directory, filename)

            # All videos have been retrieved
            if start_index >= len(channels_ids):
                # All the retrieval was completed successfully
                state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_CHANNELS_ALL_VIDEOS)
                state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_CHANNELS_RETRIEVED, True)
            else:
                print("Out of quote. Not all the channels were processed.")
        else:
            print ("Channel's ids couldn't be retrieved. Check input file.")
    except:
        print("Error on get_all_videos_by_all_channels_from_file")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return


# **********************************************************************************************************************
# **********************************************************************************************************************
def remove_duplicates(list):
    clean_list=[]
    for item in list:
        if item not in clean_list:
            clean_list.append(item)
    return clean_list

# ***********************************************************************************************************************
# Get all videos for all the channels ids in a file
# ***********************************************************************************************************************
def get_metadata_channels_from_file(youtube, filename, prefix, start_index = None):
    # Load file
    try:
        records = {}
        channels_ids_ori = get_ids_from_file(filename, "channelId")
        channels_ids = remove_duplicates(channels_ids_ori)
        if channels_ids and len(channels_ids)>0:
            state.state_yt = state.add_action(state.state_yt, state.ACTION_RETRIEVE_CHANNELS_METADATA)
            state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_CHANNELS_RETRIEVED, False)
            # Add index of the first channel to be processed
            if not start_index:
                start_index = 0

            state.state_yt = state.set_channel_index(state.state_yt, start_index)
            # Save channels_ids to be processed after if we run out of quote
            state.state_yt = state.set_channels_ids_file(state.state_yt, channels_ids)

            # Get data from YouTube API
            while (state.under_quote_limit(state.state_yt, state.UNITS_CHANNELS_LIST)) and (start_index<len(channels_ids)):
                id =channels_ids[start_index]
                print ("Obtaining metadata for channel {}".format(id))
                metadata = get_channels_metadata(youtube, [id], False)
                records[id] = metadata[id]
                start_index = start_index + 1
                state.state_yt = state.set_channel_index(state.state_yt, start_index)


            if len(records)>0:
                # Export info to excel
                directory = 'output'
                filename = get_filename_ordered(directory,prefix + "channels_metadata", 'xlsx')
                filename_path = export_dict_to_excel(records, directory, filename)
                print("Output: " + filename_path)

            # Add output filename to the list of files to merge (in case the action was not completed)
            state.add_filename_to_list(state.state_yt, state.LIST_CHANNELS_TO_MERGE, directory, filename)

            # All videos have been retrieved
            if start_index >= len(channels_ids):
                # All the retrieval was completed sucessfully
                state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_CHANNELS_METADATA)
                state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_CHANNELS_RETRIEVED, True)
            else:
                print ("Out of quote. Not all the channels were processed.")
        else:
            print("Channel's ids couldn't be retrieved. Check input file.")
    except:
        print("Error on get_channels_metadata_from_file")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return
