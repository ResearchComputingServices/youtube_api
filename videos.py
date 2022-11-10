from utils import convert_to_local_zone
from utils import export_dict_to_excel
from transcripts import get_video_transcript
from transcripts import write_transcript_to_file
import datetime
import pprint
import traceback
import sys


#-----------------------------------------------------------------------------------------------------------------------
#This function creates a dictionary that contains a video's metadata
#-----------------------------------------------------------------------------------------------------------------------
def create_video_metadata(item):

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


#-----------------------------------------------------------------------------------------------------------------------
#This function retrieves a video's metadata
#-----------------------------------------------------------------------------------------------------------------------
def get_video_metadata(youtube, video_id):

    records ={}

    #Request the video
    videos_request = youtube.videos().list(
        part="contentDetails,snippet,statistics",
        id=video_id
    )

    videos_response = videos_request.execute()

    for item in videos_response['items']:
        metadata = create_video_metadata(item)
        #pprint.pprint(metadata)
        #print ('\n')

        records[1] = metadata

    #Export info to excel
    filename = export_dict_to_excel(records, 'output', 'video_'+video_id + '_metadata.xlsx')
    print ("Output is in: " + filename)








