import traceback
import sys
from bs4 import BeautifulSoup
import os
import pathlib
import pandas as pd
import emoji
from utils import get_filename
from utils import export_dict_to_excel
from utils import export_dict_to_csv
from utils import read_excel_file_to_data_frame
from channels import get_channels_metadata



#*****************************************************************************************************
#This function gets a comment (a string) which contains html tags and/or html characters and
#returns a string without them
#*****************************************************************************************************
def soupify_comment(comment):
    soup = BeautifulSoup(comment, 'html.parser')
    return soup.get_text()

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
def get_comments_count(youtube,video_id):

    videos_request = youtube.videos().list(
        part="statistics",
        id=video_id
    )

    videos_response = videos_request.execute()
    commentsCount = 0

    for item in videos_response['items']:
        if "statistics" in item:
            commentsCount = item["statistics"].get("commentCount", "N/A")

    return commentsCount
    print ("Total comments: " + commentsCount)


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
                maxResults=100,   #Maximum is 100
                pageToken=nextPageToken
            )
            responseCommentsList = requestCommentsList.execute()
            list.extend(responseCommentsList['items'])
            nextPageToken = responseCommentsList.get('nextPageToken')
            if not nextPageToken:
                break;
    except:
        print("Error on getting replies to comment: " + parent_id)
        print(sys.exc_info()[0])
        traceback.print_exc()
    return list


#*****************************************************************************************************
#This function creates a dictionary with the comment metadata (and its replies)
#The dictionary is appended to a larger dictionary (records)
#*****************************************************************************************************
def create_comment_dict(youtube, records, item, commentsCount, comment_number):

    count = len(records)+1
    metadata={
        "id": "",
        "type":"",
        "Recipient (video or comment)":"",
        "video url" : "",
        "comment":"",
        "likeCount": "",
        "publishedAt": "",
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
            url = "https://youtu.be/" + item["snippet"].get("videoId","")
            metadata["video url"] = url
            comment = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
            if len(comment) > 0:
                comment = soupify_comment(comment)
                comment = demojize_comment(comment)
            metadata["comment"] = comment
            metadata["authorDisplayName"] = item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName", "")
            metadata["authorProfileImageUrl"] = item["snippet"]["topLevelComment"]["snippet"].get("authorProfileImageUrl",                                                                                         "")
            metadata["authorChannelId"] = item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"].get("value","")
            metadata["authorChannelUrl"] = item["snippet"]["topLevelComment"]["snippet"].get("authorChannelUrl","")
            metadata["likeCount"] = item["snippet"]["topLevelComment"]["snippet"].get("likeCount", "")
            metadata["publishedAt"] = item["snippet"]["topLevelComment"]["snippet"].get("publishedAt", "")
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
                    metadata["authorChannelUrl"] = reply["snippet"].get("authorChannelUrl", "")
                    metadata["authorDisplayName"] = reply["snippet"].get("authorDisplayName", "")
                    metadata["authorProfileImageUrl"] = reply["snippet"].get("authorProfileImageUrl", "")
                    metadata["likeCount"] = reply["snippet"].get("likeCount", "")
                    metadata["publishedAt"] = reply["snippet"].get("publishedAt", "")
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

    commentsCount = get_comments_count(youtube,video_id)
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
                maxResults=100,    #maxResults = 100
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

    count = len(records)+1
    metadata={
        "id": "",
        "type":"",
        "Recipient (video or comment)":"",
        "video url" : "",
        "comment":"",
        "likeCount": "",
        "publishedAt": "",
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
            url = "https://youtu.be/" + item["snippet"].get("videoId","")
            metadata["video url"] = url
            #metadata["original_comment"] = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay","") #debug only
            comment = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay","")
            if len(comment)>0:
                comment = soupify_comment(comment)
                comment = demojize_comment(comment)
            metadata["comment"] = comment
            metadata["authorDisplayName"] = item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName", "")
            metadata["authorProfileImageUrl"] = item["snippet"]["topLevelComment"]["snippet"].get("authorProfileImageUrl","")
            commenter_channel_id = item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"].get("value","")
            metadata["authorChannelId"] = commenter_channel_id
            metadata["authorChannelUrl"] = item["snippet"]["topLevelComment"]["snippet"].get("authorChannelUrl","")
            metadata["likeCount"] = item["snippet"]["topLevelComment"]["snippet"].get("likeCount", "")
            metadata["publishedAt"] = item["snippet"]["topLevelComment"]["snippet"].get("publishedAt", "")
            totalReplies = item["snippet"].get("totalReplyCount", "0")
            metadata["totalReplyCount"] = totalReplies
            records[count] = metadata

            if commenter_channel_id!="":
                channelId_commenters.append(commenter_channel_id)


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
                    metadata["authorChannelUrl"] = reply["snippet"].get("authorChannelUrl", "")
                    metadata["authorDisplayName"] = reply["snippet"].get("authorDisplayName", "")
                    metadata["authorProfileImageUrl"] = reply["snippet"].get("authorProfileImageUrl", "")
                    metadata["likeCount"] = reply["snippet"].get("likeCount", "")
                    metadata["publishedAt"] = reply["snippet"].get("publishedAt", "")
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



#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a single
#video given as a parameter (video_id)
#The commenters ids (channels ids) are retuned into a list of commenters
#*****************************************************************************************************
def get_single_video_comments_and_commenters(youtube, video_id, records=None, channelId_commenters=None):

    commentsCount = get_comments_count(youtube,video_id)

    if not records:
        records ={}

    if commentsCount == '0' or commentsCount == 'N/A':
        return records, channelId_commenters

    #if int(commentsCount) > 100:                      #For debugging purposes only!
    #    return records, channelId_commenters

    nextPageToken = None
    count = 0

    try:
        while True:
            # List maxResults videos in a playlist
            requestCommentsList = youtube.commentThreads().list(
                part='id,snippet,replies',
                videoId=video_id,
                maxResults=100,    #maxResults = 100
                pageToken=nextPageToken
            )

            responseCommentsList = requestCommentsList.execute()

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

    return records, channelId_commenters


#*****************************************************************************************************
#This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
#videos given as a parameter (videos_id)
#*****************************************************************************************************
def get_videos_comments_and_commenters(youtube, videos_ids, prefix_name):

    channel_records = {}
    records = {}

    try:
        channelId_commenters = []

        for video_id in videos_ids:
            print("***** Fetching comments for video " + video_id)
            records, channelId_commenters = get_single_video_comments_and_commenters(youtube, video_id, records, channelId_commenters)


        if len(records)==0 or len(channelId_commenters)==0:
            return records


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
def get_videos_comments_and_commenters_from_file(youtube,filename, prefix):
    try:
        # Load file
        df, success = read_excel_file_to_data_frame(filename, ['videoId'])
        if success:
            # Convert to list
            dfT = df.T
            videos_ids = dfT.values.tolist()
            prefix_name = "file_" + prefix + "comments_commenters"
            # Get data from YouTube API
            get_videos_comments_and_commenters(youtube, videos_ids[0], prefix_name)
            print("\n")
    except:
        print("Error on get_videos_comments_and_commenters_from_file")
        print(sys.exc_info()[0])
        traceback.print_exc()

