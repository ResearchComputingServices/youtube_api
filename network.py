import pandas as pd
from utils import export_dict_to_excel
from utils import get_filename
from utils import export_dataframe_to_excel
import pathlib
import os
from werkzeug.utils import secure_filename


def extract_data_channel_videos(records=None, directory=None, filename=None):

    if not records and not filename:
        return None

    if records:
        df = pd.DataFrame.from_dict(records, orient='index')
        #sub_info = df[['channelId', 'channel_url', 'channel_JoinDate', 'channel_viewCount',
        #               'channel_subscriberCount', 'channel_videoCount', 'videoId', 'video_title', 'video_url',
        #               'video_publishedAt', 'video_views', 'video_commentsCount']]
        df = pd.DataFrame.from_dict(records, orient='index')
        sub_info = df[['channelId', 'videoId', 'video_url']]

        return sub_info

    if filename:
        filename = os.path.join(directory, filename)
        abs_path = pathlib.Path().resolve()
        filename_fullpath = os.path.join(abs_path, filename)
        data = pd.read_excel(filename_fullpath)
        #df = pd.DataFrame(data, columns=['channelId', 'channel_url', 'channel_JoinDate', 'channel_viewCount',
        #               'channel_subscriberCount', 'channel_videoCount', 'videoId', 'video_title', 'video_url',
        #               'video_publishedAt', 'video_views', 'video_commentsCount'])
        df = pd.DataFrame(data, columns=['channelId', 'videoId', 'video_url'])

        return df


def export_channels_videos_for_network_pr(records=None, directory=None, filename=None):

    sub_info = extract_data_channel_videos(records, directory, filename)

    number_records = len(sub_info)
    source_type = ['channel' for i in range(number_records)]
    sub_info['source_type'] = source_type
    #target_type = ['video' for i in range(number_records)]
    #sub_info['target_type'] = target_type

    #sub_info.columns = ['source', 's_channel_url', 's_channel_JoinDate', 's_channel_viewCount',
    #                    's_channel_subscriberCount', 's_channel_videoCount', 'target', 't_video_title', 't_video_url',
    #                    't_video_publishedAt', 't_video_viewCounts', 't_video_commentsCount', 'source_type',
    #                    'target_type']
    sub_info.columns = ['source', 'target', 'source_type', 't_video_url']

    filename = get_filename('channels_videos_network', 'xlsx')
    export_dict_to_excel(sub_info.T, 'network', filename)
    return sub_info.to_dict()



def export_channels_videos_for_network(records=None, directory=None, filename=None):

    sub_info = extract_data_channel_videos(records, directory, filename)
    sub_info.columns = ['source', 'target',  't_video_url']

    records = sub_info.to_dict('index')
    for item in records.items():
        item[1]["source_type"] ="channel"


    filename = get_filename('channels_videos_network', 'xlsx')
    export_dict_to_excel(records, 'network', filename)
    return records




def extract_data_comments_videos_for_network(records=None, directory=None, filename=None):
    if not records and not filename:
        return None

    if records:
        df = pd.DataFrame.from_dict(records, orient='index')
        #sub_info = df[['id',	'type',	'Recipient (video or comment)',	'video url', 'publishedAt',	'totalReplyCount',
        #          'authorChannelId',	'authorChannelUrl',	'channel_JoinDate',	'channel_videoCount']]
        sub_info = df[['id', 'type', 'Recipient (video or comment)', 'video url','authorChannelId']]
        return sub_info

    if filename:
        filename = os.path.join(directory, filename)
        abs_path = pathlib.Path().resolve()
        filename_fullpath = os.path.join(abs_path, filename)
        data = pd.read_excel(filename_fullpath)
        #df = pd.DataFrame(data, columns=['id',	'type',	'Recipient (video or comment)',	'video url', 'publishedAt',	'totalReplyCount',
        #          'authorChannelId',	'authorChannelUrl',	'channel_JoinDate',	'channel_videoCount'])
        df = pd.DataFrame(data, columns=['id', 'type', 'Recipient (video or comment)', 'video url','authorChannelId'])
        return df


def export_comments_videos_for_network(records=None, directory=None, filename=None):

    sub_info = extract_data_comments_videos_for_network(records,directory,filename)


    #sub_info.columns = ["source", "source_type", "target", "t_video_url", "s_comment_publishedAt",
    #                    "s_comment_ReplyCount",
    #                    "s_commenter_channel_id", "s_commenter_channel_url", "s_commenter_channel_joinDate",
    #                    "s_commenter_video_count"]
    sub_info.columns = ["source", "source_type", "target", "t_video_url", "s_commenter_channel_id"]


    records = sub_info.to_dict('index')
    index = len(records)+1
    additional_records={}

    for item in records.items():
        d = item[1]
        metadata={}
        metadata['source']=d['s_commenter_channel_id']
        metadata['source_type']='channel'
        metadata['target'] = d['source']
        metadata['t_video_url'] = d['t_video_url']
        metadata['s_commenter_channel_id'] = d['s_commenter_channel_id']

        additional_records[index] = metadata
        index = index + 1


    records.update(additional_records)
    filename = get_filename('comment_videos_network','xlsx')
    export_dict_to_excel(records, 'network', filename)
    return records


def export_network_file_pr():

    videosFilename = "playlist_videos_channels_24_10_2022.xlsx"
    commentsFilename ="playlist_comments_channels_24_10_2022.xlsx"

    df_videos = export_channels_videos_for_network(directory="output", filename=videosFilename)
    df_comments = export_comments_videos_for_network(directory="output", filename=commentsFilename)

    dv = pd.DataFrame(df_videos)
    dc = pd.DataFrame(df_comments)
    df_merged = pd.concat([dv,dc],axis=1,ignore_index=True)
    export_dataframe_to_excel(df_merged, "network", "network3.xlsx")
    export_dict_to_excel(df_merged,"network","network2.xlsx")


    directory = "output"
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename("network4.xlsx")
    filename_path = os.path.join(full_path, filename)

    df = df_merged.T
    df.to_excel(filename_path,index=False)
    print ("x")




def export_network_file(videos_records, comments_records):

    #videosFilename = "playlist_videos_channels_24_10_2022.xlsx"
    #commentsFilename ="playlist_comments_channels_24_10_2022.xlsx"
    #df_videos = export_channels_videos_for_network(directory="output", filename=videosFilename)
    #df_comments = export_comments_videos_for_network(directory="output", filename=commentsFilename)

    df_videos = export_channels_videos_for_network(videos_records)
    df_comments = export_comments_videos_for_network(comments_records)

    dv = pd.DataFrame(df_videos)
    dc = pd.DataFrame(df_comments)
    df_merged = pd.concat([dv,dc],axis=1,ignore_index=True)

    directory = "network"
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(get_filename("network", "xlsx"))
    filename_path = os.path.join(full_path, filename)

    df = df_merged.T
    df.to_excel(filename_path,index=False)

    return filename_path


def export_network_file_2():

    videosFilename = "playlist_videos_channels_26_10_2022.xlsx"
    commentsFilename ="playlist_comments_channels_26_10_2022.xlsx"
    df_videos = export_channels_videos_for_network(directory="output", filename=videosFilename)
    df_comments = export_comments_videos_for_network(directory="output", filename=commentsFilename)

    dv = pd.DataFrame(df_videos)
    dc = pd.DataFrame(df_comments)
    df_merged = pd.concat([dv,dc],axis=1,ignore_index=True)

    directory = "network"
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(get_filename("network", "xlsx"))
    filename_path = os.path.join(full_path, filename)

    df = df_merged.T
    df.to_excel(filename_path,index=False)

    return filename_path




