from utils import read_excel_file_to_dict
from utils import convert_to_local_zone_dt
from utils import export_dict_to_excel
from utils import get_filename
import datetime
import traceback
import sys
import math


# -----------------------------------------------------------------------------------------------------------------------
# Chane any nan value in a dictionary to a specific value given as a parameter
# -----------------------------------------------------------------------------------------------------------------------
def clean_nan_from_dict(dict, new_value):
    for key, value in dict.items():
        if type(value)==float and math.isnan(value):
            dict[key] = new_value
        else:
            dict[key]=value

    return dict



#-----------------------------------------------------------------------------------------------------------------------
#This function creates a new dictionary from a dictionary with specified keys
#-----------------------------------------------------------------------------------------------------------------------
def create_dict(dict, key_name):
    new_dict = {}
    for item in dict.items():
        keyId = item[1][key_name]
        d = clean_nan_from_dict(item[1], "N/A")
        new_dict[keyId] = d
        #new_dict[keyId] = item[1]

    new_dict = clean_nan_from_dict(new_dict, "")
    return new_dict

#-----------------------------------------------------------------------------------------------------------------------
#Returns the value of a key for the first item in a dictionary
#-----------------------------------------------------------------------------------------------------------------------
def get_first_key_value(dict, key_name):
    value = None
    for item in dict.items():
        value = item[1][key_name]
        break;
    return value


#-----------------------------------------------------------------------------------------------------------------------
#This functions substract value1 - value2
#Check special conditions that may be possible in a dictionary record
#-----------------------------------------------------------------------------------------------------------------------
def substract(value1, value2, status):
    increment = 0
    if value1 != value2:
        if value1 == "N/A":
           value1 = 0
        if value2 == "N/A":
           value2 = 0
        increment = value1 - value2
        status = "CHANGED"
    return increment, status


#-----------------------------------------------------------------------------------------------------------------------
#This function compare two video records (video and creator) and returns an updated record
#-----------------------------------------------------------------------------------------------------------------------
def compare_video_records(old_item,new_item, status):
    try:
       metadata={}

       now = datetime.datetime.now()
       current_datetime_str = now.strftime("%Y-%m-%d, %H:%M:%S")


       videoId = new_item.get("videoId", "N/A")

       video_title = new_item.get("video_title", "N/A")
       if video_title!=old_item.get("video_title", "N/A"):
            video_title = "** " + video_title
            status = "CHANGED"

       video_url = new_item.get("video_url", "N/A")
       if video_url!=old_item.get("video_url","N/A"):
           video_url = "** " + video_url
           status = "CHANGED"

       video_publishedAt = new_item.get("video_publishedAt", "N/A")
       video_scrappedAt = new_item.get("video_scrappedAt", "N/A")

       video_duration = new_item.get("video_duration", "N/A")
       if video_duration!=old_item.get("video_duration","N/A"):
           video_duration = "** " + video_duration
           status = "CHANGED"

       video_views = new_item.get("video_views", 0)
       old_video_views = old_item.get("video_views", 0)
       incr_views, status = substract(video_views,old_video_views,status)

       video_likes = new_item.get("video_likes", 0)
       old_video_likes = old_item.get("video_likes", 0)
       incr_likes, status = substract(video_likes, old_video_likes,status)

       video_favoriteCount = new_item.get("video_favoriteCount", 0)
       old_video_favoriteCount = old_item.get("video_favoriteCount", 0)
       incr_favorite, status = substract(video_favoriteCount,old_video_favoriteCount,status)

       video_commentsCount = new_item.get("video_commentsCount",0)
       old_video_commentsCount = old_item.get("video_commentsCount",0)
       incr_comments, status = substract(video_commentsCount,old_video_commentsCount,status)

       video_description = new_item.get("video_description", "N/A")
       if video_description!=old_item.get("video_description", "N/A"):
           video_description = "** " + video_description
           status = "CHANGED"

       video_Transcript_Language = new_item.get("video_Transcript_Language", "N/A")
       video_Transcript_Type = new_item.get("video_Transcript_Type", "N/A")
       #video_channelId = new_item.get("video_channelId", "N/A")

       channelId = new_item.get("channelId", "N/A")
       channel_title = new_item.get("channel_title", "N/A")
       if channel_title!=old_item.get("channel_title", "N/A"):
           channel_title = "** " + channel_title
           status = "CHANGED"

       channel_description = new_item.get("channel_description", "N/A")
       old_channel_description = old_item.get("channel_description", "N/A")
       if channel_description!=old_channel_description:
           channel_description = "** " + channel_description
           status = "CHANGED"

       channel_url = new_item.get("channel_url", "N/A")
       if channel_url != old_item.get("channel_url", "N/A"):
           channel_url = "** " + channel_url
           status = "CHANGED"

       channel_JoinDate = new_item.get("channel_JoinDate", "N/A")
       channel_country = new_item.get("channel_country", "N/A")


       channel_viewCount = new_item.get("channel_viewCount", 0)
       old_channel_viewCount = old_item.get("channel_viewCount", 0)
       incr_ch_viewCount,status = substract(channel_viewCount,old_channel_viewCount,status)

       channel_subscriberCount = new_item.get("channel_subscriberCount", 0)
       old_channel_subscriberCount = old_item.get("channel_subscriberCount", 0)
       incr_ch_suscriberCount,status = substract(channel_subscriberCount,old_channel_subscriberCount,status)

       channel_videoCount = new_item.get("channel_videoCount", 0)
       old_channel_videoCount = old_item.get("channel_videoCount", 0)
       incr_ch_videoCount, status= substract(channel_videoCount,old_channel_videoCount,status)



       metadata = {
            "videoId": videoId,
            "video_title": video_title,
            "video_url": video_url,
            "video_publishedAt": video_publishedAt,
            "video_scrappedAt": video_scrappedAt,
            "video_comparedAt": current_datetime_str,
            "video_duration": video_duration,
            "video_views": video_views,
            "update_video_views": incr_views,
            "video_likes": video_likes,
            "update_video_likes": incr_likes,
            "video_favoriteCount": video_favoriteCount,
            "update_video_favoriteCount":incr_favorite,
            "video_commentsCount": video_commentsCount,
            "upate_video_commentsCount" : incr_comments,
            "video_description": video_description,
            "video_Transcript Language": video_Transcript_Language,
            "video_Transcript Type": video_Transcript_Type,
            "channelId": channelId,
            "channel_title" : channel_title,
            "channel_description" : channel_description,
            "channel_url" : channel_url,
            "channel_JoinDate" : channel_JoinDate,
            "channel_country" : channel_country,
            "channel_viewCount": channel_viewCount,
            "update_channel_viewCount" : incr_ch_viewCount,
            "channel_suscriberCount" : channel_subscriberCount,
            "update_channel_suscriberCount" : incr_ch_suscriberCount,
            "channel_videoCount":channel_videoCount,
            "update_channel_videoCount" : incr_ch_videoCount,
            "status": status,
       }
    except:
        print("Error on creating dict: \n")
        print(sys.exc_info()[0])
        traceback.print_exc()
    return metadata



#-----------------------------------------------------------------------------------------------------------------------
#This function returns two dictionaries newer and older which contains the most recent and older, respetively, files.
#The dictionaries key will correspond to the id sent as parameter
#-----------------------------------------------------------------------------------------------------------------------
def get_newer_and_older_dicts(file1, file2, scrapped_header, id):

    try:
        # Step 1. Load files into dictionaries
        dict1 = read_excel_file_to_dict(file1)
        dict2 = read_excel_file_to_dict(file2)

        # Step 2. Get newet file
        date1 = get_first_key_value(dict1, scrapped_header)
        date2 = get_first_key_value(dict2, scrapped_header)

        date1_dt = convert_to_local_zone_dt(date1)
        date2_dt = convert_to_local_zone_dt(date2)

        if date2_dt > date1_dt:
            newer_dict = create_dict(dict2, id)
            older_dict = create_dict(dict1, id)
        else:
            newer_dict = create_dict(dict1, id)
            older_dict = create_dict(dict2, id)
    except:
        newer_dict=None
        older_dict=None

    return newer_dict, older_dict


#-----------------------------------------------------------------------------------------------------------------------
#This function compare two excel files with video_creators info and outputs a file with the difference between them.
#-----------------------------------------------------------------------------------------------------------------------
def compare_video_creators_files(file1, file2, user_prefix):

    records = {}
    newer_dict, older_dict= get_newer_and_older_dicts(file1, file2, "video_scrappedAt", "videoId")

    if not newer_dict or not older_dict:
        print ("There was an error processing the input files.")
        return

    for new_key, new_item in newer_dict.items():
        # Locate item in older_dict
        old_item = older_dict.get(new_key)
        status = "NO CHANGES"
        if not old_item:
            # Video record was not in older file
            old_item = new_item
            status = "NEW VIDEO"

        updated_record = compare_video_records(old_item, new_item, status)
        records[new_key] = updated_record

    # Export info to excel
    directory = 'output'
    filename = get_filename('comparison_' + user_prefix + '_videos_creators', 'xlsx')
    filename = export_dict_to_excel(records, directory, filename)
    print('Output: ' + filename)


#-----------------------------------------------------------------------------------------------------------------------
#This function compare two excel files with video_creators info and outputs a file with the difference between them.
#-----------------------------------------------------------------------------------------------------------------------
def compare_comments_commenters_files(file1, file2, user_prefix):

    records={}

    print ("Pre-processing comment files...")
    newer_dict, older_dict = get_newer_and_older_dicts(file1, file2, "scrappedAt", "id")

    if not newer_dict or not older_dict:
        print ("There was an error processing the input files.")
        return

    print ("Comparing new comments  vs old comments...")
    for new_key, new_item in newer_dict.items():
        #Locate item in older_dict
        old_item=older_dict.get(new_key)
        if not old_item:
            #Comment is new (it wasn't retrieved before)
            records[new_key]=new_item

    # Export info to excel
    total_new_comments = len(records)
    total_new_comments_perc = (total_new_comments/len(newer_dict))*100
    directory = 'output'
    filename = get_filename('comparison_recent_' + user_prefix + '_comments_commenters', 'xlsx')
    filename = export_dict_to_excel(records, directory, filename)
    print('Output: ' + filename)

    records = {}
    print ("Comparing old comments vs new comments...")
    for old_key, old_item in older_dict.items():
        #Locate item in older_dict
        new_item=newer_dict.get(old_key)
        if not new_item:
            #Comment is new (it wasn't retrieved before)
            records[old_key]=old_item


    total_old_comments = len(records)
    total_old_comments_perc = (total_old_comments / len(older_dict)) * 100

    # Export info to excel
    directory = 'output'
    filename = get_filename('comparison_older_'+ user_prefix + '_comments_commenters', 'xlsx')
    filename = export_dict_to_excel(records, directory, filename)
    print('Output: ' + filename)

    common_comments = len(newer_dict)-total_new_comments
    common_comments_perc = (common_comments/len(newer_dict))*100

    print ("There are " + str(total_old_comments) +  " deleted comments " + str(round(total_old_comments_perc,2)) + "%" )
    print ("There are " + str(total_new_comments) +  " new comments " +  str(round(total_new_comments_perc,2)) + "%")
    print ("Total common comments: " + str(common_comments) + " " +  str(round(common_comments_perc,2)) + "%")

    if (common_comments)!=(len(older_dict)-total_old_comments):
        print ("Inconsistency in common comments between files. Double check input files.")