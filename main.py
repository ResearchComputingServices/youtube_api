from services import *
import argparse
import sys
from playlists import get_playlist_metadata
from playlists import get_playlist_videos_comments
from playlists import get_playlist_video_and_channels_metadata
from playlists import get_playlist_comments_and_channels_metadata
from channels import get_all_videos_by_a_channel_metadata
from channels import get_channels_metadata
from search import get_videos_by_keyword_metadata
from videos import get_video_metadata
from comments import get_video_comments
from network import export_comments_videos_for_network

if __name__ == "__main__":

    option=""
    youtube = build_service_oauth()

    if not youtube:
        print("Error when creating API Youtube service.")
        sys.exit()

    while (option.upper()!="X"):
        print ('\n-------------------- Options --------------------\n')

        print ("[1]: PLAYLIST: Videos' METADATA and TRANSCRIPT")
        print ("[2]: PLAYLIST: Video's COMMENTS")
        print ("[3]: PLAYLIST: Videos' METADATA, TRANSCRIPT and CHANNEL creator)")
        print ("[4]: PLAYLIST: Videos' COMMENTS and CHANNEL commenter")
        print ("[5]: CHANNEL:  Metadata")
        print ("[6]: CHANNEL:  Videos")
        print ("[7]: KEYWORDS: Videos' METADATA")
        print ("[8]: VIDEO: Metadata and transcript")
        print ("[9]: VIDEO: Comments")
        print ("[X]: Exit")

        option = input ("Please introduce your option: ")
        #option="10"

        if not option:
            print('An option should be provided.')
            sys.exit()

        #Get all videos' metadata from playlist in config.
        if option == "1":
            playlist = get_url_playlist()
            get_playlist_metadata(youtube, playlist)


        #Get all comments for all the videos on a playlist
        if option  == "2":
            playlist = get_url_playlist()
            get_playlist_videos_comments(youtube, playlist)

        #Get videos and channels metadata
        if option == "3":
            playlist = get_url_playlist()
            get_playlist_video_and_channels_metadata(youtube, playlist)


        # Get videos and channels metadata
        if option == "4":
            playlist = get_url_playlist()
            get_playlist_comments_and_channels_metadata(youtube, playlist)


        if option == "5":
            ch_id = input("Introduce channel id: ")
            channel_ids = [ch_id]
            get_channels_metadata(youtube, channel_ids, True)


        if option == "6":
            channel_id = input("Introduce channel id: ")
            get_all_videos_by_a_channel_metadata(youtube, channel_id)


        if option == "7":
            query = input("Enter your keyword search: ")
            get_videos_by_keyword_metadata(youtube, query)


        if option=="8":
            video_id = input ("Introduce video id: ")
            get_video_metadata(youtube, video_id)


        if option=="9":
            video_id = input ("Introduce video id: ")
            records = get_video_comments(youtube, video_id, None)
            export_dict_to_excel(records, 'output', 'video_' + video_id + '_comments.xlsx')
            print ("Output is in " + 'video_' + video_id + '_comments.xlsx')

        if option =="10":
            export_comments_videos_for_network('output','playlist_comments_channels_metadata.xlsx')
            option = "X"


        #To get channel metadata for a list of channels
        #channel_ids = ["UCfz0X0J88di_4xIQHf-BI1Q"]
        #get_channels_metadata(youtube, channel_ids, True)












