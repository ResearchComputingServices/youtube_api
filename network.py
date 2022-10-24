import pandas as pd
from utils import export_dict_to_excel
from utils import get_filename
import pathlib
import os


def extract_data_channel_videos(records=None, directory=None, filename=None):

    if not records and not filename:
        return None

    if records:
        df = pd.DataFrame.from_dict(records, orient='index')
        sub_info = df[['channelId', 'channel_url', 'channel_JoinDate', 'channel_viewCount',
                       'channel_subscriberCount', 'channel_videoCount', 'videoId', 'video_title', 'video_url',
                       'video_publishedAt', 'video_views', 'video_commentsCount']]
        return sub_info

    if filename:
        filename = os.path.join(directory, filename)
        abs_path = pathlib.Path().resolve()
        filename_fullpath = os.path.join(abs_path, filename)
        data = pd.read_excel(filename_fullpath)
        df = pd.DataFrame(data, columns=['channelId', 'channel_url', 'channel_JoinDate', 'channel_viewCount',
                       'channel_subscriberCount', 'channel_videoCount', 'videoId', 'video_title', 'video_url',
                       'video_publishedAt', 'video_views', 'video_commentsCount'])

        return df


def export_channels_videos_for_network(records=None, directory=None, filename=None):

    sub_info = extract_data_channel_videos(records, directory, filename)

    number_records = len(sub_info)
    source_type = ['channel' for i in range(number_records)]
    sub_info['source_type'] = source_type
    target_type = ['video' for i in range(number_records)]
    sub_info['target_type'] = target_type

    sub_info.columns = ['source', 's_channel_url', 's_channel_JoinDate', 's_channel_viewCount',
                        's_channel_subscriberCount', 's_channel_videoCount', 'target', 't_video_title', 't_video_url',
                        't_video_publishedAt', 't_video_viewCounts', 't_video_commentsCount', 'source_type',
                        'target_type']

    filename = get_filename('channels_videos_network', 'xlsx')
    export_dict_to_excel(sub_info.T, 'network', filename)




def extract_data_comments_videos_for_network(records=None, directory=None, filename=None):
    if not records and not filename:
        return None

    if records:
        df = pd.DataFrame.from_dict(records, orient='index')
        sub_info = df[['id',	'type',	'Recipient (video or comment)',	'video url', 'publishedAt',	'totalReplyCount',
                  'authorChannelId',	'authorChannelUrl',	'channel_JoinDate',	'channel_videoCount']]
        return sub_info

    if filename:
        filename = os.path.join(directory, filename)
        abs_path = pathlib.Path().resolve()
        filename_fullpath = os.path.join(abs_path, filename)
        data = pd.read_excel(filename_fullpath)
        df = pd.DataFrame(data, columns=['id',	'type',	'Recipient (video or comment)',	'video url', 'publishedAt',	'totalReplyCount',
                  'authorChannelId',	'authorChannelUrl',	'channel_JoinDate',	'channel_videoCount'])

        return df


def export_comments_videos_for_network(records=None, directory=None, filename=None):

    sub_info = extract_data_comments_videos_for_network(records,directory,filename)

    sub_info.columns = ["source", "source_type", "target", "t_video_url", "s_comment_publishedAt",
                        "s_comment_ReplyCount",
                        "s_commenter_channel_id", "s_commenter_channel_url", "s_commenter_channel_joinDate",
                        "s_commenter_video_count"]


    records = sub_info.to_dict('index')
    index = len(records)+1
    additional_records={}

    for item in records.items():
        d = item[1]
        metadata={}
        metadata['source']=d['s_commenter_channel_id']
        metadata['source_type']='channel'
        metadata['target'] = d['source']
        metadata['s_commenter_channel_url'] = d['s_commenter_channel_url']
        metadata['s_commenter_channel_joinDate'] = d['s_commenter_channel_joinDate']
        metadata['s_commenter_video_count'] = d['s_commenter_video_count']

        additional_records[index] = metadata
        index = index + 1


    records.update(additional_records)
    filename = get_filename('comment_videos_network','xlsx')
    export_dict_to_excel(records, 'network', filename)






