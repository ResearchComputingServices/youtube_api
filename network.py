import pandas as pd
from utils import export_dict_to_excel
from utils import get_filename
from utils import read_excel_file_to_data_frame
import pathlib
import os
import sys
import traceback
import state
from werkzeug.utils import secure_filename

#-----------------------------------------------------------------------------------------------------------------------
#This functions extracts specific columns about videos and channel's (creator) from a file or from a set of records
#These columns will be used in the merged file that will correspond to the network
#-----------------------------------------------------------------------------------------------------------------------
def extract_data_channel_videos(records=None, filename=None):

    success = False

    if not records and not filename:
        return None, success

    if records:
        df = pd.DataFrame.from_dict(records, orient='index')
        sub_info = df[['channelId', 'videoId', 'video_url', 'video_views', 'video_commentsCount']]
        success = True
        return sub_info, success

    if filename:
        df, success = read_excel_file_to_data_frame(filename, columns=['channelId', 'videoId', 'video_url', 'video_views', 'video_commentsCount'])
        return df, success


#-----------------------------------------------------------------------------------------------------------------------
#This function export channel and videos column to an excel file
#This function may be merged with the previous function into a single one.
#-----------------------------------------------------------------------------------------------------------------------
def export_channels_videos_for_network(records=None, filename=None):

    try:
        output = None
        sub_info, success = extract_data_channel_videos(records=records, filename=filename)

        if success:
            sub_info.columns = ['source', 'target',  't_video_url', 't_video_views', 't_video_comments_count']
            output = sub_info.to_dict('index')
            for item in output.items():
                item[1]["source_type"] ="channel"

            #filename = get_filename('channels_videos_network', 'xlsx')
            #export_dict_to_excel(output, 'network', filename)
    except:
        print ("Error on export_channels_videos_for_network")

    return output

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def extract_data_comments_videos_for_network(records=None, filename=None):

    success = False

    if not records and not filename:
        return None, success

    if records:
        df = pd.DataFrame.from_dict(records, orient='index')
        sub_info = df[['id', 'type', 'Recipient (video or comment)', 'video url','authorChannelId']]
        success = True
        return sub_info, success

    if filename:
        df, success = read_excel_file_to_data_frame(filename, columns=['id', 'type', 'Recipient (video or comment)', 'video url','authorChannelId'])
        return df, success

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def export_comments_videos_for_network(records=None, filename=None):

    try:
        output = None
        sub_info, success = extract_data_comments_videos_for_network(records=records,filename=filename)
        if success:
            sub_info.columns = ["source", "source_type", "target", "t_video_url", "s_commenter_channel_id"]
            output = sub_info.to_dict('index')
            index = len(output)+1
            additional_records={}

            for item in output.items():
                d = item[1]
                metadata={}
                metadata['source']=d['s_commenter_channel_id']
                metadata['source_type']='channel'
                metadata['target'] = d['source']
                metadata['t_video_url'] = d['t_video_url']
                metadata['s_commenter_channel_id'] = d['s_commenter_channel_id']

                additional_records[index] = metadata
                index = index + 1


            output.update(additional_records)
            #filename = get_filename('comment_videos_network','xlsx')
            #export_dict_to_excel(records, 'network', filename)
    except:
        print ("Error on export_comments_videos_for_network")

    return output

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def export_network_file(prefix_name, videos_records=None, comments_records=None, videosFilename=None, commentsFilename=None):

    filename_path = ""
    try:
        if videos_records and comments_records:
            df_videos = export_channels_videos_for_network(records=videos_records)
            df_comments = export_comments_videos_for_network(records=comments_records)
        else:
            if videosFilename and commentsFilename:
                df_videos = export_channels_videos_for_network(filename=videosFilename)
                df_comments = export_comments_videos_for_network(filename=commentsFilename)
            else:
                return filename_path

        if (not df_videos) or (not df_comments):
            print ("Error when creating network.")
            return filename_path

        dv = pd.DataFrame(df_videos)
        dc = pd.DataFrame(df_comments)
        df_merged = pd.concat([dv,dc],axis=1,ignore_index=True)

        directory = "network"
        abs_path = pathlib.Path().resolve()
        full_path = os.path.join(abs_path, directory)
        filename = secure_filename(get_filename(prefix_name + "_network", "xlsx"))
        filename_path = os.path.join(full_path, filename)

        df = df_merged.T
        df.to_excel(filename_path,index=False)
        state.remove_action(state.state_yt, state.ACTION_CREATE_NETWORK)
    except:
        print("Error on export_network_file ")
        print(sys.exc_info()[0])
        traceback.print_exc()


    return filename_path






