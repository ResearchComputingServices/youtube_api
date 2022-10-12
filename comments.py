import traceback
import sys



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
            metadata["comment"] = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay","")
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

                if len(item["replies"])<int(totalReplies):
                    #Get all replies
                    print ("Getting all replies")
                    replies = get_comments_replies(youtube, item["id"])
                else:
                    replies = item["replies"]["comments"]

                print ("Total replies: " + str(len(replies)))

                for reply in replies:
                    comment_number = comment_number + 1
                    metadata = {}
                    count = count + 1
                    metadata["id"] = reply["id"]
                    metadata["type"] = "Reply to comment"
                    metadata["Recipient (video or comment)"] = reply["snippet"].get("parentId", "")
                    metadata["comment"] = reply["snippet"].get("textDisplay", "")
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


def get_comments_replies(youtube, parent_id):

    nextPageToken = None
    pages = 0

    list =[]
    try:
        while True:

            pages = pages + 1

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
            #if not nextPageToken or pages == 2:
            if not nextPageToken:
                break;
    except:
        print("Error on getting replies to comment: " + parent_id)
        print(sys.exc_info()[0])
        traceback.print_exc()

    return list


def get_video_comments(youtube, video_id, records=None):

    commentsCount = get_comments_count(youtube,video_id)
    #print ('Comments count: ' + str(commentsCount))

    if not records:
        records ={}

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
                print('Comment {}'.format(count))
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



def create_comment_and_channel_dict(youtube, records, item, commentsCount, comment_number, channelId_commenters):

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
            metadata["comment"] = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay","")
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

                if len(item["replies"])<int(totalReplies):
                    #Get all replies
                    print ("Getting all replies")
                    replies = get_comments_replies(youtube, item["id"])
                else:
                    replies = item["replies"]["comments"]

                print ("Total replies: " + str(len(replies)))

                for reply in replies:
                    comment_number = comment_number + 1
                    metadata = {}
                    count = count + 1
                    metadata["id"] = reply["id"]
                    metadata["type"] = "Reply to comment"
                    metadata["Recipient (video or comment)"] = reply["snippet"].get("parentId", "")
                    metadata["comment"] = reply["snippet"].get("textDisplay", "")
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


def get_video_comments_and_channels(youtube, video_id, records=None, channelId_commenters=None):

    commentsCount = get_comments_count(youtube,video_id)
    #print ('Comments count: ' + str(commentsCount))

    if not records:
        records ={}

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
                print('Comment {}'.format(count))
                before = len(records)
                records, channelId_commenters = create_comment_and_channel_dict(youtube, records, item, commentsCount, count, channelId_commenters)
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

    return records, channelId_commenters