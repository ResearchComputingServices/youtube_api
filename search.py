import traceback
import sys
import state
from comments import get_videos_comments_and_commenters
from channels import get_videos_and_videocreators
from network import export_network_file
from videos import create_video_metadata
from utils import get_filename
from utils import export_dict_to_excel



#*****************************************************************************************************
#This function executes a search on youtube (similar to the one in youtube search bar) to retrieves
#the videos that match the query given as a paramter.
#The search is based on relevance to the query
#*****************************************************************************************************
def get_videos_id_by_query(youtube, query, numberVideosToRetrieve):
    nextPageToken = None
    videos_ids=[]

    maxResults = state.MAX_SEARCH_RESULTS_PER_REQUEST
    if numberVideosToRetrieve<maxResults:
        maxResults = numberVideosToRetrieve

    count = 0
    try:
        while True:
            if not state.under_quote_limit(state.state_yt,state.UNITS_SEARCH_LIST):
                return

            video_channels_request = youtube.search().list(
                part="snippet",
                q=query,
                type="video",
                maxResults=maxResults,
                order="relevance",
                pageToken=nextPageToken

            )
            response_videos_channels = video_channels_request.execute()
            state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_SEARCH_LIST)

            # Obtain video_id for each video in the response
            for item in response_videos_channels['items']:
                videoId = item["id"].get("videoId", "N/A")
                videos_ids.append(videoId)
                count = count + 1

            nextPageToken = response_videos_channels.get('nextPageToken')
            if not nextPageToken or count >= numberVideosToRetrieve:
                # if not nextPageToken:
                break;

    except:
        print("Error on get_videos_id_by_query")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return videos_ids

#*****************************************************************************************************
#This functions searches for the videos that matches a query in youtube
#It returns the metadata for the files
#*****************************************************************************************************
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
                maxResults=state.MAX_SEARCH_RESULTS_PER_REQUEST,
                order="relevance",
                pageToken=nextPageToken

            )
            response_videos_channels = video_channels_request.execute()
            state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_SEARCH_LIST)

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
            state.state_yt = state.update_quote_usage(state.state_yt, state.UNITS_VIDEOS_LIST)

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
        print("Error on get_videos_by_keyword_metadata ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    # Export info to excel
    #export_dict_to_excel(records, 'queries_videos.xlsx')
    filename = get_filename('videos_query_metadata','xlsx')
    export_dict_to_excel(records, 'output', filename)
    print ("Output is in: " + filename)

#*****************************************************************************************************
#This function searches videos on youtube that match a query (by relevance)
#The argument network specifies if the whole network will be built (videos and parameters).
# To build a network, videos, creators, comments and commenters are needed.
#If the network parameter is None, the function will only retrieve videos and its creators.
#only the videos and its creators will be retrieved.
#The maxNumberVideos given as parameter is optional. The default is 100. This parameter should be
#on multiples of 50.
#*****************************************************************************************************
def search_videos_youtube(youtube, query, maxNumberVideos=None, network=None):
    print ("Executing query/YouTube search ")

    videos_with_quote = state.number_of_items_with_quote(state.UNITS_SEARCH_LIST, state.MAX_SEARCH_RESULTS_PER_REQUEST)
    if (not maxNumberVideos) or (maxNumberVideos<0) or (maxNumberVideos >videos_with_quote):
        if state.DEFAULT_VIDEOS_TO_RETRIEVE < videos_with_quote:
            maxNumberVideos=  state.DEFAULT_VIDEOS_TO_RETRIEVE
        else:
            maxNumberVideos = videos_with_quote

    cost = state.total_requests_cost(maxNumberVideos,state.MAX_SEARCH_RESULTS_PER_REQUEST,state.UNITS_SEARCH_LIST)
    proceed = input ("Search {} videos for query \"{}\" with a cost of {} units [Y/N]? ".format(maxNumberVideos,query,cost))
    if proceed.upper() != "Y":
        sys.exit()


    videos_ids = get_videos_id_by_query(youtube, query,maxNumberVideos)
    videos_ids = list(set(videos_ids))

    if videos_ids and len(videos_ids)>0:
        state.add_action(state.state_yt, state.ACTION_RETRIEVE_VIDEOS)

        if network:
            state.add_action(state.state_yt, state.ACTION_RETRIEVE_COMMENTS)
            state.add_action(state.state_yt, state.ACTION_CREATE_NETWORK)

        print ('Getting video and creators metadata ')
        videos_records = get_videos_and_videocreators(youtube, videos_ids, "search_" + query + "_videos_creators")

        if network:
            print ('Getting comments and commenters metadata ')
            comments_records = get_videos_comments_and_commenters(youtube, videos_ids, "search_" + query + "_comments_commenters")
            print ('Exporting network file ')
            output_file = export_network_file("search_" + query, videos_records=videos_records, comments_records=comments_records)
            if output_file and len(output_file)>0:
                print("Output is in :" + output_file)


