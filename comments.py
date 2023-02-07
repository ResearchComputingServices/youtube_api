import traceback
import sys
from bs4 import BeautifulSoup
import os
import pathlib
import pandas as pd
import emoji
import datetime
import state
from utils import get_filename
from utils import export_dict_to_excel
from utils import export_dict_to_csv
from utils import get_fullpath
from utils import export_csv_to_excel
from utils import get_ids_from_file
from utils import get_filename_ordered
from utils import remove_prefix_url
from channels import get_channels_metadata




#*****************************************************************************************************
#This function gets a comment (a string) which contains html tags and/or html characters and
#returns a string without them
#*****************************************************************************************************
def soupify_comment(comment):
    return comment
    #soup = BeautifulSoup(comment, 'html.parser')
    #return soup.get_text()

#*****************************************************************************************************
#This functions gets a comment (a string) and replaces the emojis with the emoji name and  the prefix
#"emoji_"
#*****************************************************************************************************
def demojize_comment(comment):
    return emoji.demojize(comment,delimiters=(" emoji_", " "))


#*****************************************************************************************************
#To delete
#*****************************************************************************************************
def demo():
    filename ="commentsS.xlsx"
    directory = "output"
    if filename:
        filename = os.path.join(directory, filename)
        abs_path = pathlib.Path().resolve()
        filename_fullpath = os.path.join(abs_path, filename)
        data = pd.read_excel(filename_fullpath)
        # df = pd.DataFrame(data, columns=['channelId', 'channel_url', 'channel_JoinDate', 'channel_viewCount',
        #               'channel_subscriberCount', 'channel_videoCount', 'videoId', 'video_title', 'video_url',
        #               'video_publishedAt', 'video_views', 'video_commentsCount'])
        df = pd.DataFrame(data, columns=['comment'])

        dict = df.to_dict()
        dict2 = dict['comment']
        for key, comment in dict2.items():
            #print ("Cleaning comment: ")
            comment = soupify_comment(comment)
            print ("\n Demojize comment: ")
            demojize_comment(comment)




#*****************************************************************************************************
#This function retrieves the total comments (including replies) for a video (video_id)
#*****************************************************************************************************
def _get_comments_count(youtube, videos_ids):

    videos_request = youtube.videos().list(
        part="statistics",
        id=','.join(videos_ids)
    )
    videos_response = videos_request.execute()
    state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_VIDEOS_LIST)

    comments_count = {}
    for item in videos_response['items']:
        if "statistics" in item:
            id = item["id"]
            commentsCount = item["statistics"].get("commentCount", "N/A")
            comments_count[id] = commentsCount

    return comments_count


#*****************************************************************************************************
#This function retrieves the total comments (including replies) for a list of videos ids
#*****************************************************************************************************
def get_comments_count(youtube,videos_ids):

    comments_count = {}
    slice = True
    start = 0
    while (slice):
        end = start + state.MAX_JOIN_VIDEOS_IDS
        if end > len(videos_ids):
            end = len(videos_ids)
            slice = False
        r = _get_comments_count(youtube, videos_ids[start:end])
        comments_count.update(r)
        start = end
    return comments_count

#*****************************************************************************************************
#This function retrieves the replies for a comment (parent_id)
#*****************************************************************************************************
def get_comment_replies(youtube, parent_id):

    nextPageToken = None
    list =[]
    try:
        while True:
            # List maxResults videos in a playlist
            requestCommentsList = youtube.comments().list(
                part='id,snippet',
                parentId = parent_id,
                maxResults=state.MAX_REPLIES_PER_REQUEST,
                textFormat='plainText',
                pageToken=nextPageToken
            )
            responseCommentsList = requestCommentsList.execute()
            state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_COMMENTS_LIST)
            list.extend(responseCommentsList['items'])
            nextPageToken = responseCommentsList.get('nextPageToken')
            if not nextPageToken:
                break;
    except:
        print("Error on getting replies to comment: " + parent_id)
        print(sys.exc_info()[0])
        traceback.print_exc()
        list=[]

    return list


#*****************************************************************************************************
#This function creates a dictionary with the comment metadata (and its replies)
#The dictionary is appended to a larger dictionary (records)
#*****************************************************************************************************
def create_comment_dict(youtube, records, item, commentsCount, comment_number):

    now = datetime.datetime.now()
    current_datetime_str = now.strftime("%Y-%m-%d, %H:%M:%S")

    count = len(records)+1
    metadata={
        "id": "",
        "type":"",
        "Recipient (video or comment)":"",
        "video url" : "",
        "comment":"",
        "likeCount": "",
        "publishedAt": "",
        "scrappedAt" : "",
        "totalReplyCount": "",
        "authorDisplayName": "",
        "authorProfileImageUrl": "",
        "authorChannelId": "",
        "authorChannelUrl" :"",
        "totalComments" : commentsCount,
        "comment #": comment_number,
    }

    if "snippet" in item:
        try:
            metadata["id"] = item["id"]
            metadata["type"] = "Comment to video"
            metadata["Recipient (video or comment)"] = item["snippet"].get("videoId","")
            #url = "https://youtu.be/" + item["snippet"].get("videoId","")
            url = "youtu.be/" + item["snippet"].get("videoId", "")
            metadata["video url"] = url
            comment = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
            if len(comment) > 0:
                comment = soupify_comment(comment)
                comment = demojize_comment(comment)
            metadata["comment"] = comment
            metadata["authorDisplayName"] = item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName", "")
            metadata["authorProfileImageUrl"] = remove_prefix_url(item["snippet"]["topLevelComment"]["snippet"].get("authorProfileImageUrl"),                                                                                         "")
            metadata["authorChannelId"] = item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"].get("value","")
            metadata["authorChannelUrl"] = remove_prefix_url(item["snippet"]["topLevelComment"]["snippet"].get("authorChannelUrl",""))
            metadata["likeCount"] = item["snippet"]["topLevelComment"]["snippet"].get("likeCount", "")
            metadata["publishedAt"] = item["snippet"]["topLevelComment"]["snippet"].get("publishedAt", "")
            metadata["scrappedAt"] = current_datetime_str
            totalReplies = item["snippet"].get("totalReplyCount", "0")
            metadata["totalReplyCount"] = totalReplies
            records[count] = metadata



            if "replies" in item:

                if len(item["replies"]["comments"])<int(totalReplies):
                    replies = get_comment_replies(youtube, item["id"])
                else:
                    replies = item["replies"]["comments"]

                for reply in replies:
                    comment_number = comment_number + 1
                    metadata = {}
                    count = count + 1
                    metadata["id"] = reply["id"]
                    metadata["type"] = "Reply to comment"
                    metadata["Recipient (video or comment)"] = reply["snippet"].get("parentId", "")

                    comment = reply["snippet"].get("textDisplay", "")
                    if len(comment) > 0:
                        comment = soupify_comment(comment)
                        comment = demojize_comment(comment)

                    metadata["comment"] = comment
                    metadata["authorChannelId"] = reply["snippet"]["authorChannelId"].get("value", "")
                    metadata["authorChannelUrl"] = remove_prefix_url(reply["snippet"].get("authorChannelUrl", ""))
                    metadata["authorDisplayName"] = reply["snippet"].get("authorDisplayName", "")
                    metadata["authorProfileImageUrl"] = reply["snippet"].get("authorProfileImageUrl", "")
                    metadata["likeCount"] = reply["snippet"].get("likeCount", "")
                    metadata["publishedAt"] = reply["snippet"].get("publishedAt", "")
                    metadata["scrappedAt"] = current_datetime_str
                    metadata["totalReplyCount"] = "N/A"
                    metadata["video url"]= ""
                    metadata["totalComments"] = commentsCount
                    metadata["comment #"] = comment_number

                    records[count] = metadata
        except:
            print("Error on creating comment dictionary for video: " + item["id"])
            print(sys.exc_info()[0])
            traceback.print_exc()

    else:
        records[count] = metadata

    return records



#*****************************************************************************************************
#This function gets all the comments for a video (video_id) and returns these comments in a dictioanry
#of dictionaries
#*****************************************************************************************************
def get_video_comments(youtube, video_id, records=None):

    count = get_comments_count(youtube, [video_id])
    commentsCount = count[video_id]
    #print ('Comments count: ' + str(commentsCount))

    if not records:
        records ={}

    if commentsCount=='0' or commentsCount=='N/A':
        return records

    nextPageToken = None
    pages = 0
    count = 0


    try:
        while True:

            pages = pages + 1

            # List maxResults videos in a playlist
            requestCommentsList = youtube.commentThreads().list(
                part='id,snippet,replies',
                videoId=video_id,
                maxResults=state.MAX_COMMENTS_PER_REQUEST,    #maxResults = 100
                textFormat = 'plainText',
                pageToken=nextPageToken
            )

            responseCommentsList = requestCommentsList.execute()

            for item in responseCommentsList['items']:
                count = count + 1
                before = len(records)
                records = create_comment_dict(youtube, records, item, commentsCount, count)
                replies = len(records) - before - 1
                count = count + replies
                nextPageToken = responseCommentsList.get('nextPageToken')

            #if not nextPageToken or pages == 1:
            if not nextPageToken:
                break;
    except:
        print("Error on getting video comments: " + video_id)
        print(sys.exc_info()[0])
        traceback.print_exc()

    return records





#*****************************************************************************************************
#This function creates a dictionary with the comment metadata (and its replies)
#The dictionary is appended to a larger dictionary (records)
#The function also adds the commenter id (channel id) to a list of channels (channelId_commenters)
#*****************************************************************************************************
def create_comment_and_commenter_dict(youtube, records, item, commentsCount, comment_number, channelId_commenters):


    now = datetime.datetime.now()
    current_datetime_str = now.strftime("%Y-%m-%d, %H:%M:%S")

    count = len(records)+1
    #print ("Comment " + str(count))
    metadata={
        "id": "",
        "type":"",
        "Recipient (video or comment)":"",
        "video url" : "",
        "comment":"",
        "likeCount": "",
        "publishedAt": "",
        "scrappedAt": "",
        "totalReplyCount": "",
        "authorDisplayName": "",
        "authorProfileImageUrl": "",
        "authorChannelId": "",
        "authorChannelUrl" :"",
        "totalComments" : commentsCount,
        "comment #": comment_number,
    }

    if "snippet" in item:
        try:
            metadata["id"] = item["id"]
            metadata["type"] = "Comment"
            metadata["Recipient (video or comment)"] = item["snippet"].get("videoId","")
            #url = "https://youtu.be/" + item["snippet"].get("videoId","")
            url = "youtu.be/" + item["snippet"].get("videoId", "")
            metadata["video url"] = url
            #metadata["original_comment"] = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay","") #debug only
            comment = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay","")
            if len(comment)>0:
                comment = soupify_comment(comment)
                comment = demojize_comment(comment)
            metadata["comment"] = comment
            metadata["authorDisplayName"] = item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName", "")
            metadata["authorProfileImageUrl"] = remove_prefix_url(item["snippet"]["topLevelComment"]["snippet"].get("authorProfileImageUrl",""))
            commenter_channel_id = item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"].get("value","")
            metadata["authorChannelId"] = commenter_channel_id
            metadata["authorChannelUrl"] = remove_prefix_url(item["snippet"]["topLevelComment"]["snippet"].get("authorChannelUrl",""))
            metadata["likeCount"] = item["snippet"]["topLevelComment"]["snippet"].get("likeCount", "")
            metadata["publishedAt"] = item["snippet"]["topLevelComment"]["snippet"].get("publishedAt", "")
            metadata["scrappedAt"] = current_datetime_str
            totalReplies = item["snippet"].get("totalReplyCount", "0")
            metadata["totalReplyCount"] = totalReplies
            records[count] = metadata

            if commenter_channel_id!="":
                channelId_commenters.append(commenter_channel_id)


            if "replies" in item:

                copy_replies = True
                if len(item["replies"]["comments"])<int(totalReplies):
                    replies_retrieving_cost = state.total_requests_cost(int(totalReplies), state.MAX_REPLIES_PER_REQUEST, state.UNITS_COMMENTS_LIST)
                    #We only retrieve replies if we have enough quote
                    #These calls are difficult to estimate in advance, since we don't know for which videos we will
                    #actually get all the replies in the first call.
                    if state.under_quote_limit(state.state_yt,replies_retrieving_cost):
                        replies = get_comment_replies(youtube, item["id"])
                        #We actually obtained more replies than the first call
                        if len(replies)>0 and len(replies)>len(item["replies"]["comments"]):
                            copy_replies = False

                if copy_replies:
                    replies = item["replies"]["comments"]

                for reply in replies:
                    comment_number = comment_number + 1
                    metadata = {}
                    count = count + 1
                    metadata["id"] = reply["id"]
                    metadata["type"] = "Reply"
                    metadata["Recipient (video or comment)"] = reply["snippet"].get("parentId", "")
                    #metadata["original_comment"] = reply["snippet"].get("textDisplay", "")  #debug only
                    comment = reply["snippet"].get("textDisplay", "")
                    if len(comment) > 0:
                        comment = soupify_comment(comment)
                        comment = demojize_comment(comment)
                    metadata["comment"] = comment
                    commenter_channel_id = reply["snippet"]["authorChannelId"].get("value", "")
                    metadata["authorChannelId"] = commenter_channel_id
                    metadata["authorChannelUrl"] = remove_prefix_url(reply["snippet"].get("authorChannelUrl", ""))
                    metadata["authorDisplayName"] = reply["snippet"].get("authorDisplayName", "")
                    metadata["authorProfileImageUrl"] = remove_prefix_url(reply["snippet"].get("authorProfileImageUrl", ""))
                    metadata["likeCount"] = reply["snippet"].get("likeCount", "")
                    metadata["publishedAt"] = reply["snippet"].get("publishedAt", "")
                    metadata["scrappedAt"] = current_datetime_str
                    metadata["totalReplyCount"] = "N/A"
                    metadata["video url"]= ""
                    metadata["totalComments"] = commentsCount
                    metadata["comment #"] = comment_number

                    if commenter_channel_id != "":
                        channelId_commenters.append(commenter_channel_id)

                    records[count] = metadata
        except:
            print("Error on creating comment dictionary for video: " + item["id"])
            print(sys.exc_info()[0])
            traceback.print_exc()

    else:
        records[count] = metadata

    return records, channelId_commenters



#***********************************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a single
#video given as a parameter (video_id)
#The commenters ids (channels ids) are retuned into a list of commenters
#***********************************************************************************************************************
def get_single_video_comments_and_commenters(youtube, video_id, commentsCount, records=None, channelId_commenters=None):

    if not records:
        records ={}

    if commentsCount == 0 or commentsCount == 'N/A':
        return records, channelId_commenters

    #if int(commentsCount) > 100:                      #For debugging purposes only!
    #    return records, channelId_commenters

    nextPageToken = None
    count = 0

    try:
        fully_retrieved = True
        while True:
            if not state.under_quote_limit(state.state_yt, state.UNITS_COMMENTS_THREADS_LIST):
                fully_retrieved = False
                break

            # List maxResults videos in a playlist
            requestCommentsList = youtube.commentThreads().list(
                part='id,snippet,replies',
                videoId=video_id,
                maxResults=state.MAX_COMMENTS_PER_REQUEST,    #maxResults = 100
                textFormat='plainText',
                pageToken=nextPageToken
            )

            responseCommentsList = requestCommentsList.execute()
            state.state_yt = state.update_quote_usage(state.state_yt,state.UNITS_COMMENTS_THREADS_LIST)

            for item in responseCommentsList['items']:
                count = count + 1
                before = len(records)
                records, channelId_commenters = create_comment_and_commenter_dict(youtube, records, item, commentsCount, count, channelId_commenters)
                replies = len(records) - before - 1
                count = count + replies
                nextPageToken = responseCommentsList.get('nextPageToken')
            if not nextPageToken:
                break;
    except:
        print("Error on getting video comments: " + video_id)
        print(sys.exc_info()[0])
        traceback.print_exc()

    return records, channelId_commenters, fully_retrieved


#*****************************************************************************************************
#This function removes from a list the videos form whom the cost of retrieving all its comments
#superpases the available quote
#It also removes videos with zero or N/A comments
#*****************************************************************************************************
def filter_videos_by_comments_count(comments_count_original):
    comments_count ={}
    for video_id, total_comments in comments_count_original.items():
        if not (total_comments  == '0' or total_comments == 'N/A'):
            cost = state.total_requests_cost(int(total_comments),state.MAX_COMMENTS_PER_REQUEST,state.UNITS_COMMENTS_LIST)
            if cost < 10000:
                #if cost < state.UNITS_QUOTE_LIMIT:
                comments_count[video_id] =  int(total_comments)
            else:
                print ("Video {} has {} comments. It cannot be retrieved with current quote. ".format(video_id,total_comments))
                #Save to file to notify user - TO DO
    return comments_count

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def _sort_by_comment_count(comments_dict):
    d = {k: v for k, v in sorted(comments_dict.items(), key=lambda x: x[1])}

    #sorted_list  = sorted(comments_dict.items(), key=lambda x: x[1])
    #d = dict (sorted_list)
    return d


#*****************************************************************************************************
#This funtion retrieves the # of comments for a list of videos ids
#Returns a dictionary list where the key is the video id.
#Sorts the list (by default) from min to max number of comments
#*****************************************************************************************************
def obtain_total_comments_for_videos_ids(youtube, videos_ids, sort=False):

    try:
        #Cost of retrieving videos
        cost = state.total_requests_cost(len(videos_ids), state.MAX_VIDEOS_PER_REQUEST, state.UNITS_VIDEOS_LIST)
        if not state.under_quote_limit(state.state_yt, cost):
            return None, None

        #Obtain the total comments per video_id
        videos_comments_count_original = get_comments_count(youtube, videos_ids)

        #Remove the un-retrievable videos, i.e., videos for we cannot retrieve their comments with the
        #full available quote (the cost of retrieving the comments superpasses the available quote)
        #It also removes videos with zero or N/A comments
        videos_comments_count = filter_videos_by_comments_count(videos_comments_count_original)

        #Update the videos_id only with the videos that we can actually retrieve
        videos_ids = list(videos_comments_count.keys())

        #Sort the list by default
        if sort==True:
            videos_comments_count = _sort_by_comment_count(videos_comments_count)

        state.state_yt = state.set_videos_ids_file(state.state_yt, videos_ids)
        state.state_yt = state.set_videos_comments_count_file(state.state_yt, videos_comments_count)
    except:
        print("Error on obtaining total comments for videos ids" )
        print(sys.exc_info()[0])
        traceback.print_exc()
        return None, None

    return videos_ids, videos_comments_count

#*****************************************************************************************************
#This function calculates the maximum number of videos to retrieve comments for
#with the current quote
#*****************************************************************************************************
def get_max_number_videos_to_retrieve_comments(comments_count, start_index, upper_bound=None):

    video_counter = 0
    sub_dict = comments_count.items()[start_index:len(comments_count.items())]

    for video_id, comments_count in sub_dict.items():
        #Note we are asumming that all replies will be comming together with the comments
        cost = cost + state.total_requests_cost(comments_count, state.MAX_COMMENTS_PER_REQUEST, state.UNITS_COMMENTS_LIST)
        channels_cost = int(video_counter / state.MAX_CHANNELS_PER_REQUEST) + 1

        if state.under_quote_limit(state.state_yt, cost + state.UNITS_CHANNELS_LIST * channels_cost):
            video_counter = video_counter + 1
            if upper_bound and video_counter > upper_bound:
                break

    return video_counter


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def _save_subcomments(records, directory, filename, mode='w', index=True, header=True):
    df = pd.DataFrame.from_dict(records, orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    filename_path = export_dict_to_csv(sub_info, directory, filename, mode, index, header)
    return filename_path



#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def _save_state_csv(start_index,directory, prefix_name):
    # Save state action
    state.state_yt = state.add_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)
    # Save start index for retrieving comments
    state.state_yt = state.set_comment_index(state.state_yt, start_index)

    filename_comments_xlsx = get_filename_ordered(directory, prefix_name, 'xlsx')
    filename_comments_csv = get_filename_ordered(directory, prefix_name, 'csv')
    filename_subcomments = get_filename_ordered(directory, prefix_name +'_SUB','csv')
    state.add_filename_to_list(state.state_yt, state.LIST_COMMENTS_TO_MERGE, directory, filename_comments_xlsx)
    state.add_filename_to_list(state.state_yt, state.LIST_SUBCOMMENTS_TO_MERGE, directory, filename_subcomments)

    return filename_comments_xlsx, filename_comments_csv, filename_subcomments


#-----------------------------------------------------------------------------------------------------------------------
#This function saves to the state the start_index, the action (retrieve comments)
#The filenames of the output
#-----------------------------------------------------------------------------------------------------------------------
def _save_to_state(start_index,directory,prefix_name):

    # Save state action
    state.state_yt = state.add_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)
    state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_COMMENTS_RETRIEVED, False)
    # Save start index for retrieving comments
    state.state_yt = state.set_comment_index(state.state_yt, start_index)

    #Save filename to states
    filename_comments = get_filename_ordered(directory, prefix_name, 'xlsx')
    filename_subcomments = get_filename_ordered(directory, prefix_name +'_SUB','csv')

    return filename_comments, filename_subcomments


#*****************************************************************************************************
#*****************************************************************************************************
def _sum_comments_count(comments_count, start):
    try:
        _sum = sum(comments_count.values(),start)
    except:
        _sum = 0
    return _sum


#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters(youtube, videos_ids, prefix_name, videos_comments_count=None, start_index = None):

    channel_records = {}
    records = {}
    filename_records_path =""
    filename_subrecords_path = ""

    if not start_index:
       start_index = 0

    directory = 'output'
    filename_comments, filename_subcomments = _save_to_state(start_index, directory, prefix_name)
    #state.print_state(state.state_yt)

    #Retrieve the comment count per video (if not preivously retrieved)
    if not videos_comments_count:
        videos_ids, videos_comments_count =  obtain_total_comments_for_videos_ids(youtube, videos_ids)
        if not videos_ids or not videos_comments_count:
            return records


    _total_comments = _sum_comments_count(videos_comments_count,start_index)
    if _total_comments>0:
        retrieving_cost = state.total_requests_cost(_total_comments,state.MAX_COMMENTS_PER_REQUEST,state.UNITS_COMMENTS_THREADS_LIST)
        print ("Retrieving {} comments' metadata with at least a cost of {} units".format(_total_comments,retrieving_cost))

    while (start_index < len(videos_ids)):
        try:
            channelId_commenters = []
            inc = 0
            while (len(channelId_commenters) < state.MAX_CHANNELS_PER_REQUEST) and (start_index+inc < len(videos_ids)):
                video_id = videos_ids[start_index + inc]
                video_id_comments_count = videos_comments_count[video_id]
                comments_cost = state.total_requests_cost(video_id_comments_count, state.MAX_COMMENTS_PER_REQUEST, state.UNITS_COMMENTS_LIST)
                commenters_cost = state.total_requests_cost(video_id_comments_count, state.MAX_CHANNELS_PER_REQUEST, state.UNITS_CHANNELS_LIST)

                fully_retrieved = False
                #We do not have enough quote to retrieve the comments for this video along with its commenter's info
                if not state.under_quote_limit(state.state_yt,comments_cost+commenters_cost):
                    print ("There is no enough quote to continue retrieving comments.")
                    break

                print("***** Fetching comments for video: " + video_id)
                records, channelId_commenters, fully_retrieved = get_single_video_comments_and_commenters(youtube, video_id, videos_comments_count[video_id], records, channelId_commenters)
                if not fully_retrieved:
                    # The videos's comments were not fully retrieved because we run out of quote while retrieving some
                    # of the comments
                    print("There is no enough quote to continue retrieving comments.")
                    break

                inc = inc + 1
                channelId_commenters = list(set(channelId_commenters))

            if not fully_retrieved:
                break

            if len(records)==0 or len(channelId_commenters)==0:
                return records

            #Check that we have quote to retrieve commenters
            commenters_cost = state.total_requests_cost(len(channelId_commenters), state.MAX_CHANNELS_PER_REQUEST,
                                                        state.UNITS_CHANNELS_LIST)
            if not state.under_quote_limit(state.state_yt,commenters_cost):
                print("There is no enough quote to continue retrieving comments.")
                break

            #Retrieving channel info
            print("*** Fetching commenters info")
            # Get commenter's channels metadata
            # We request at most 50 channels at the time to avoid breaking the API
            slice = True
            start = 0
            while (slice):
                end = start + state.MAX_CHANNELS_PER_REQUEST
                if end > len(channelId_commenters):
                    end = len(channelId_commenters)
                    slice = False
                r = get_channels_metadata(youtube, channelId_commenters[start:end], False)
                channel_records.update(r)
                start = end

            for key, item in records.items():
                try:
                    channel_id_commenter = item["authorChannelId"]
                    channel_info = channel_records[channel_id_commenter]
                    item.update(channel_info)
                except:
                    print ('Error on: ' + channel_id_commenter)

            start_index = start_index + inc

        except:
            print("Error on getting video comments and commenters")
            print(sys.exc_info()[0])
            traceback.print_exc()

    print("\n")

    if len(records)>0:
        # Export info to excel
        print("*** Saving Info")

        filename_records_path = export_dict_to_excel(records, directory, filename_comments)
        filename_subrecords_path = _save_subcomments(records, directory, filename_subcomments)
        state.state_yt = state.set_comment_index(state.state_yt, start_index)
        state.add_filename_to_list(state.state_yt, state.LIST_COMMENTS_TO_MERGE, directory, filename_comments)
        state.add_filename_to_list(state.state_yt, state.LIST_SUBCOMMENTS_TO_MERGE, directory, filename_subcomments)

    if len(filename_records_path)>0:
        print("Output: " + filename_records_path)
        print ("Output: "  +filename_subrecords_path)

    if start_index>=len(videos_ids):
        #All videos were retrieved
        state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)
        state.state_yt = state.set_all_retrieved(state.state_yt, state.ALL_COMMENTS_RETRIEVED, True)



    #export_comments_videos_for_network(records)
    return records









#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters_4(youtube, videos_ids, prefix_name, videos_comments_count=None, start_index = None):

    channel_records = {}
    records = {}
    filename_records_path =""
    filename_subrecords_path = ""

    if not start_index:
       start_index = 0

    directory = 'output'
    filename_comments, filename_subcomments = _save_to_state(start_index, directory, prefix_name)
    #state.print_state(state.state_yt)

    #Retrieve the comment count per video (if not preivously retrieved)
    if not videos_comments_count:
        videos_ids, videos_comments_count =  obtain_total_comments_for_videos_ids(youtube, videos_ids)
        if not videos_ids or not videos_comments_count:
            return records


    _total_comments = +_sum_comments_count(videos_comments_count,start_index)
    if _total_comments>0:
        retrieving_cost = state.total_requests_cost(_total_comments,state.MAX_COMMENTS_PER_REQUEST,state.UNITS_COMMENTS_THREADS_LIST)
        print ("Retrieving {} comments' metadata with at least a cost of {} units".format(_total_comments,retrieving_cost))

    while (start_index < len(videos_ids)):
        try:
            channelId_commenters = []
            inc = 0
            while (len(channelId_commenters) < state.MAX_CHANNELS_PER_REQUEST) and (start_index+inc < len(videos_ids)):
                video_id = videos_ids[start_index + inc]
                video_id_comments_count = videos_comments_count[video_id]
                comments_cost = state.total_requests_cost(video_id_comments_count, state.MAX_COMMENTS_PER_REQUEST, state.UNITS_COMMENTS_LIST)
                commenters_cost = state.total_requests_cost(video_id_comments_count, state.MAX_CHANNELS_PER_REQUEST, state.UNITS_CHANNELS_LIST)

                fully_retrieved = False
                #We do not have enough quote to retrieve the comments for this video along with its commenter's info
                if not state.under_quote_limit(state.state_yt,comments_cost+commenters_cost):
                    print ("There is no enough quote to continue retrieving comments.")
                    break

                print("***** Fetching comments for video: " + video_id)
                records, channelId_commenters, fully_retrieved = get_single_video_comments_and_commenters(youtube, video_id, videos_comments_count[video_id], records, channelId_commenters)
                if not fully_retrieved:
                    # The videos's comments were not fully retrieved because we run out of quote while retrieving some
                    # of the comments
                    print("There is no enough quote to continue retrieving comments.")
                    break

                inc = inc + 1
                channelId_commenters = list(set(channelId_commenters))

            if not fully_retrieved:
                break

            if len(records)==0 or len(channelId_commenters)==0:
                return records



            #Check that we have quote to retrieve commenters
            commenters_cost = state.total_requests_cost(len(channelId_commenters), state.MAX_CHANNELS_PER_REQUEST,
                                                        state.UNITS_CHANNELS_LIST)
            if not state.under_quote_limit(state.state_yt,commenters_cost):
                print("There is no enough quote to continue retrieving comments.")
                break

            #Retrieving channel info
            print("*** Fetching commenters info")
            # Get commenter's channels metadata
            # We request at most 50 channels at the time to avoid breaking the API
            slice = True
            start = 0
            while (slice):
                end = start + state.MAX_CHANNELS_PER_REQUEST
                if end > len(channelId_commenters):
                    end = len(channelId_commenters)
                    slice = False
                r = get_channels_metadata(youtube, channelId_commenters[start:end], False)
                channel_records.update(r)
                start = end

            for key, item in records.items():
                try:
                    channel_id_commenter = item["authorChannelId"]
                    channel_info = channel_records[channel_id_commenter]
                    item.update(channel_info)
                except:
                    print ('Error on: ' + channel_id_commenter)

            #Export info to excel
            print ("*** Saving Info")
            filename_records_path = export_dict_to_excel(records, directory, filename_comments)
            filename_subrecords_path = _save_subcomments(records,directory,filename_subcomments)

            #Videos' comments and commenters were sucessfully retrieved and saved to disk
            #Save state
            start_index = start_index + inc
            state.state_yt = state.set_comment_index(state.state_yt, start_index)
            state.add_filename_to_list(state.state_yt, state.LIST_COMMENTS_TO_MERGE, directory, filename_comments)
            state.add_filename_to_list(state.state_yt, state.LIST_SUBCOMMENTS_TO_MERGE, directory, filename_subcomments)

        except:
            print("Error on getting video comments and commenters")
            print(sys.exc_info()[0])
            traceback.print_exc()

    print("\n")

    if len(filename_records_path)>0:
        print("Output: " + filename_records_path)
        print ("Output: "  +filename_subrecords_path)

    if start_index>=len(videos_ids):
        #All videos were retrieved
        state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)


    #export_comments_videos_for_network(records)
    return records




#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters_to_csv(youtube, videos_ids, prefix_name, videos_comments_count=None, start_index = None):

    records = {}

    if not start_index:
       start_index = 0

    directory = 'output'
    filename_comments_xlsx, filename_comments_csv, filename_subcomments = _save_state(start_index, directory, prefix_name)
    state.print_state(state.state_yt)

    #Retrieve the comment count per video (if not preivously retrieved)
    if not videos_comments_count:
        videos_ids, videos_comments_count =  obtain_total_comments_for_videos_ids(youtube, videos_ids)
        if not videos_ids or not videos_comments_count:
            return records

    first_time = True
    while (start_index < len(videos_ids)):
        try:
            channelId_commenters = []
            records = {}
            channel_records = {}
            inc = 0
            while (len(channelId_commenters) < state.MAX_CHANNELS_PER_REQUEST) and (start_index+inc < len(videos_ids)):
                video_id = videos_ids[start_index + inc]
                video_id_comments_count = videos_comments_count[video_id]
                comments_cost = state.total_requests_cost(video_id_comments_count, state.MAX_COMMENTS_PER_REQUEST, state.UNITS_COMMENTS_LIST)
                commenters_cost = state.total_requests_cost(video_id_comments_count, state.MAX_CHANNELS_PER_REQUEST, state.UNITS_CHANNELS_LIST)

                fully_retrieved = False
                #We do not have enough quote to retrieve the comments for this video along with its commenter's info
                if not state.under_quote_limit(state.state_yt,comments_cost+commenters_cost):
                    break

                print("***** Fetching comments for video: " + video_id)
                records, channelId_commenters, fully_retrieved = get_single_video_comments_and_commenters(youtube, video_id, videos_comments_count[video_id], records, channelId_commenters)
                if not fully_retrieved:
                    # The videos's comments were not fully retrieved because we run out of quote while retrieving some
                    # of the comments
                    break

                inc = inc + 1
                channelId_commenters = list(set(channelId_commenters))

            if not fully_retrieved:
                break


            if len(records)==0 or len(channelId_commenters)==0:
                return records



            #Check that we have quote to retrieve commenters
            if not state.under_quote_limit(state.state_yt,commenters_cost):
               break

            #Retrieving channel info
            print("*** Fetching commenters info")
            # Get commenter's channels metadata
            # We request at most 50 channels at the time to avoid breaking the API
            slice = True
            start = 0
            while (slice):
                end = start + state.MAX_CHANNELS_PER_REQUEST
                if end > len(channelId_commenters):
                    end = len(channelId_commenters)
                    slice = False

                if len(channelId_commenters[start:end]) > 0:
                    r = get_channels_metadata(youtube, channelId_commenters[start:end], False)
                    channel_records.update(r)

                start = end

            for key, item in records.items():
                try:
                    channel_id_commenter = item["authorChannelId"]
                    channel_info = channel_records[channel_id_commenter]
                    item.update(channel_info)
                except:
                    print ('Error on: ' + channel_id_commenter)

            #Export info to excel
            print ("*** Saving Info")
            if first_time:
                #Create the first time the file
                first_time = False
                filename_comments_path = export_dict_to_csv(records, directory, filename_comments_csv, mode='w',
                                                           index=True, header=True)
                filename_subcomments_path = _save_subcomments(records, directory, filename_subcomments, mode='w',
                                                           index=True, header=True)

            else:
                #Append afterwards (not elegant :-|, I know)
                filename_comments_path = export_dict_to_csv(records, directory, filename_comments_csv, mode='a',
                                                           index=True, header=False)
                filename_subcomments_path = _save_subcomments(records, directory, filename_subcomments, mode='a',
                                                           index=True, header=False)

            #Videos' comments and commenters were sucessfully retrieved and saved to disk
            #Save state
            start_index = start_index + inc
            state.state_yt = state.set_video_index(state.state_yt, start_index)

        except:
            print("Error on getting video comments and commenters")
            print(sys.exc_info()[0])
            traceback.print_exc()

    print("\n")

    print("Output: " + get_fullpath(directory,filename_comments_xlsx))
    print ("Output: "  +filename_subcomments_path)

    export_csv_to_excel(filename_comments_path,get_fullpath(directory,filename_comments_xlsx))
    #Remove CSV files to avoid excess of files.
    #delete_file(filename_comments_csv_path)


    if start_index>=len(videos_ids):
        #All videos were retrieved
        state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)


    #export_comments_videos_for_network(records)
    return records

#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters_3(youtube, videos_ids, prefix_name, videos_comments_count=None, start_index = None):

    MAX_CHANNELS_PER_REQUEST = 50
    COMMENTS_PER_REQUEST = 100

    channel_records = {}
    records = {}

    if not start_index:
       start_index = 0

    directory = 'output'
    filename_records, filename_subrecords = _save_state(start_index, directory, prefix_name)
    state.print_state(state.state_yt)

    #Take a look to get max videos to retrieve
    #Lets try to maximize the number of channels calls/requests
    #Retrieve the comments count for each video
    if not videos_comments_count:
        #We need to save in the state the comments count as well!
        #ahhh this is getting so convoluted!
        videos_ids, videos_comments_count =  obtain_total_comments_for_videos_ids(youtube, videos_ids)
        #The comments' count couldn't being retrieved with the current quote
        if not videos_ids or not videos_comments_count:
            return records


    while (start_index < len(videos_ids)):
        try:
            channelId_commenters = []
            video_id = videos_ids[start_index]  #Notice that video_id will have the videos with no comments or giantic comments. We need to update this.
            video_id_comments_count = videos_comments_count[video_id]
            comments_cost = state.total_requests_cost(video_id_comments_count, COMMENTS_PER_REQUEST, state.UNITS_COMMENTS_LIST)
            commenters_cost = state.total_requests_cost(video_id_comments_count, MAX_CHANNELS_PER_REQUEST, state.UNITS_CHANNELS_LIST)

            #We do not have enough quote to retrieve the comments for this video along with its commenter's info
            if not state.under_quote_limit(state.state_yt,comments_cost+commenters_cost):
                break

            print("***** Fetching comments for video: " + video_id)
            records, channelId_commenters, fully_retrieved = get_single_video_comments_and_commenters(youtube, video_id, videos_comments_count[video_id], records, channelId_commenters)
            if not fully_retrieved:
                # The videos's comments were not fully retrieved because we run out of quote while retrieving some
                # of the comments
                break


            if len(records)==0 or len(channelId_commenters)==0:
                return records

            channelId_commenters = list(set(channelId_commenters))

            #Check that we have quote to retrieve commenters
            if not state.under_quote_limit(state.state_yt,commenters_cost):
               break

            #Retrieving channel info
            print("*** Fetching commenters info")
            # Get commenter's channels metadata
            # We request at most 50 channels at the time to avoid breaking the API
            slice = True
            start = 0
            while (slice):
                end = start + MAX_CHANNELS_PER_REQUEST
                if end > len(channelId_commenters):
                    end = len(channelId_commenters)
                    slice = False
                r = get_channels_metadata(youtube, channelId_commenters[start:end], False)
                channel_records.update(r)
                start = end

            for key, item in records.items():
                try:
                    channel_id_commenter = item["authorChannelId"]
                    channel_info = channel_records[channel_id_commenter]
                    item.update(channel_info)
                except:
                    print ('Error on: ' + channel_id_commenter)

            #Export info to excel
            print ("*** Saving Info")
            filename_records_path = export_dict_to_excel(records, directory, filename_records)
            filename_subrecords_path = _save_subcomments(records,directory,filename_subrecords)

            #Videos' comments and commenters were sucessfully retrieved and saved to disk
            #Save state
            start_index = start_index + 1
            state.state_yt = state.set_video_index(state.state_yt, start_index)
        except:
            print("Error on getting video comments and commenters")
            print(sys.exc_info()[0])
            traceback.print_exc()

    print("\n")

    print("Output: " + filename_records_path)
    print ("Output: "  +filename_subrecords_path)

    if start_index>=len(videos_ids):
        #All videos were retrieved
        state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)


    #export_comments_videos_for_network(records)
    return records

#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters_2(youtube, videos_ids, prefix_name, videos_comments_count=None, start_index = None):

    MAX_CHANNELS_PER_REQUEST = 50

    channel_records = {}
    records = {}

    if not start_index:
       start_index = 0

    directory = 'output'
    filename_records, filename_subrecords = _save_state(start_index, directory, prefix_name)
    state.print_state(state.state_yt)

    #Retrieve the comments count for each video
    if not videos_comments_count:
        #We need to save in the state the comments count as well!
        #ahhh this is getting so convoluted!
        videos_ids, videos_comments_count =  obtain_total_comments_for_videos_ids(youtube, videos_ids)
        #The comments' count couldn't being retrieved with the current quote
        if not videos_ids or not videos_comments_count:
            return records

    #We need to make this loop using the sorted comments_count instead of videos_ids
    #AND this changes how we save videos_ids to a file videos_ids_temp.xlsx
    #we will not preserve the order

    retrieving = True
    while (start_index < len(videos_ids)) and (retrieving):
        try:
            i = 0
            channelId_commenters = []
            retrieving = True
            while ((start_index < len(videos_ids)) and ((i < MAX_CHANNELS_PER_REQUEST) or (retrieving==True))):
                COMMENTS_PER_REQUEST = 100
                video_id = videos_ids[start_index]  #Notice that video_id will have the videos with no comments or giantic comments. We need to update this.
                video_id_comments_count = videos_comments_count[video_id]
                comments_cost = state.total_requests_cost(video_id_comments_count, COMMENTS_PER_REQUEST, state.UNITS_COMMENTS_LIST)
                commenters_cost = state.total_requests_cost(video_id_comments_count, MAX_CHANNELS_PER_REQUEST, state.UNITS_CHANNELS_LIST)
                fully_retrieved = False
                if state.under_quote_limit(state.state_yt,comments_cost+commenters_cost):
                    print("***** Fetching comments for video " + video_id)
                    records, channelId_commenters, fully_retrieved = get_single_video_comments_and_commenters(youtube, video_id, videos_comments_count[video_id], records, channelId_commenters)
                    if not fully_retrieved:
                        # The videos's comments were not fully retrieved. That is, we run out of quote while retrieving some
                        # of the comments
                        retrieving = False
                    else:
                        start_index = start_index + 1
                    i=i+1
                else:
                    retrieving = False

            if len(records)==0 or len(channelId_commenters)==0:
                return records

            channelId_commenters = list(set(channelId_commenters))
            commenters_cost = state.total_requests_cost(len(channelId_commenters), MAX_CHANNELS_PER_REQUEST, state.UNITS_CHANNELS_LIST)
            if state.under_quote_limit(state.state_yt,commenters_cost):
                #Retrieving channel info
                print("Getting channels info")
                # Get commenter's channels metadata
                # We request at most 50 channels at the time to avoid breaking the API
                slice = True
                start = 0
                while (slice):
                    end = start + MAX_CHANNELS_PER_REQUEST
                    if end > len(channelId_commenters):
                        end = len(channelId_commenters)
                        slice = False
                    r = get_channels_metadata(youtube, channelId_commenters[start:end], False)
                    channel_records.update(r)
                    start = end

                for key, item in records.items():
                    try:
                        channel_id_commenter = item["authorChannelId"]
                        channel_info = channel_records[channel_id_commenter]
                        item.update(channel_info)
                    except:
                        print ('Error on: ' + channel_id_commenter)

                #Export info to excel
                #Use an ordered file name (but create it outside this loop)
                #Save state the name of the output file in comments to merge
                filename_records_path = export_dict_to_excel(records, directory, filename_records)
                filename_subrecords_path = _save_subcomments(records,directory,filename_subrecords)
                state.state_yt = state.set_video_index(state.state_yt, start_index)
            else:
                retrieving = False
        except:
            print("Error on getting video comments and commenters")
            print(sys.exc_info()[0])
            traceback.print_exc()

    print("\n")

    print("Output: " + filename_records_path)
    print ("Output: "  +filename_subrecords_path)

    if start_index>=len(videos_ids):
        #All videos were retrieved
        state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)


    #export_comments_videos_for_network(records)
    return records



#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters_1(youtube, videos_ids, prefix_name, videos_comments_count=None, start_index = None):

    MAX_CHANNELS_PER_REQUEST = 50

    channel_records = {}
    records = {}

    if not start_index:
       start_index = 0

    directory = 'output'
    filename_records, filename_subrecords = _save_state(start_index, directory, prefix_name)
    state.print_state(state.state_yt)

    #Retrieve the comments count for each video
    if not videos_comments_count:
        #We need to save in the state the comments count as well!
        #ahhh this is getting so convoluted!
        videos_comments_count =  obtain_total_comments_for_videos_ids(youtube, videos_ids)
        #The comments' count couldn't being retrieved with the current quote
        if not videos_comments_count:
            return records

    channelId_commenters = []
    while (start_index < len(videos_ids)):
        try:
            max_videos = get_max_number_videos_to_retrieve_comments(videos_comments_count, start_index, MAX_CHANNELS_PER_REQUEST)
            # There is no enough quote to continue retrieving comments
            if max_videos==0:
                break

            #Retrieve all comments for max_videos
            i = 0
            while (i < max_videos):
                video_id = videos_ids[start_index]
                start_index = start_index + 1
                print("***** Fetching comments for video " + video_id)
                records, channelId_commenters = get_single_video_comments_and_commenters(youtube, video_id, videos_comments_count[video_id], records, channelId_commenters)
                i=i+1

            if len(records)==0 or len(channelId_commenters)==0:
                return records

            #Retrieving channel info
            print ("Getting channels info")
            channelId_commenters = list(set(channelId_commenters))
            r = get_channels_metadata(youtube, channelId_commenters, False)
            channel_records.update(r)

            #slice = True
            #start = 0
            #while (slice):
            #    end = start + 50
            #    if end > len(channelId_commenters):
            #        end=len(channelId_commenters)
            #        slice = False
            #    r = get_channels_metadata(youtube, channelId_commenters[start:end], False)
            #    channel_records.update(r)
            #    start = end

            if len(records)>0:
                for key, item in records.items():
                    try:
                        channel_id_commenter = item["authorChannelId"]
                        channel_info = channel_records[channel_id_commenter]
                        item.update(channel_info)
                    except:
                        print ('Error on: ' + channel_id_commenter)

            #Export info to excel
            #Use an ordered file name (but create it outside this loop)
            #Save state the name of the output file in comments to merge
            filename_records_path = export_dict_to_excel(records, directory, filename_records)
            filename_subrecords_path = _save_subcomments(records,directory,filename_subrecords)

        except:
            print("Error on getting video comments and commenters")
            print(sys.exc_info()[0])
            traceback.print_exc()

    print("\n")

    if len(filename_records_path)>0:
        print("Output: " + filename_records_path)
        print ("Output: "  +filename_subrecords_path)

    if start_index>=len(videos_ids):
        #All videos were retrieved
        state.state_yt = state.remove_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)


    #export_comments_videos_for_network(records)
    return records

#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters_before_state(youtube, videos_ids, prefix_name):

    channel_records = {}
    records = {}

    try:
        channelId_commenters = []

        for video_id in videos_ids:
            print("***** Fetching comments for video " + video_id)
            records, channelId_commenters = get_single_video_comments_and_commenters(youtube, video_id, records, channelId_commenters)


        if len(records)==0 or len(channelId_commenters)==0:
            return records

        print ("Getting channels info")
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
        print("Error on getting video comments and commenters")
        print(sys.exc_info()[0])
        traceback.print_exc()

    print("\n")

    # Export info to excel
    directory = 'output'
    filename = get_filename(prefix_name,'xlsx')
    filename = export_dict_to_excel(records, directory, filename)
    print("Output: " + filename)

    filename = get_filename(prefix_name +'_SUB','csv')
    df = pd.DataFrame.from_dict(records, orient='index')
    sub_info = df[['id', 'Recipient (video or comment)', 'comment']].T
    filename = export_dict_to_csv(sub_info, directory, filename)
    print ("Output: "  +filename)

    #export_comments_videos_for_network(records)
    return records



#*****************************************************************************************************
#This function retrieves all comments, its replies, and its commenters ids (channel id) for a list of
#videosId extracted from a file given as a parameter (filename)
#Note that this file should have a column with a heading videoId
#*****************************************************************************************************
def get_videos_comments_and_commenters_from_file(youtube,filename, prefix, videos_comments_count_filename=None, start_index=None):
    try:
        # Load file
        videos_ids = get_ids_from_file(filename, "videoId")
        if videos_ids:
            prefix_name = "file_" + prefix + "_comments_commenters"
            # Get data from YouTube API
            videos_comments_count=None
            if videos_comments_count_filename:
                videos_comments_count = state.get_videos_comments_count_file(videos_comments_count_filename)
            get_videos_comments_and_commenters(youtube, videos_ids, prefix_name, videos_comments_count, start_index)
            print("\n")
    except:
        print("Error on get_videos_comments_and_commenters_from_file")
        print(sys.exc_info()[0])
        traceback.print_exc()

