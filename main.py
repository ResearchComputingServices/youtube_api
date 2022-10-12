from services import *
import argparse
import sys
from playlists import get_playlist_metadata
from playlists import get_playlist_comments
from playlists import get_playlist_video_and_channels_metadata
from playlists import get_playlist_comments_and_channels_metadata
from channels import get_channel_videos_metadata
from channels import get_channels_metadata
from search import get_videos_by_keyword_metadata
from videos import get_video_metadata
from comments import get_video_comments

if __name__ == "__main__":

    option=""
    youtube = build_service_oauth()

    if not youtube:
        print("Error when creating API Youtube service.")
        sys.exit()

    while (option.upper()!="X"):
        print ('Options: \n')

        print ("[1]: PLAYLIST: Videos' METADATA and TRANSCRIPT")
        print ("[2]: PLAYLIST: Video's COMMENTS")
        print ("[3]: CHANNEL:  Metadata")
        print ("[4]: CHANNEL:  Videos")
        print ("[5]: KEYWORDS: Videos' METADATA")
        print ("[6]: VIDEO: Metadata and transcript")
        print ("[7]: VIDEO: Comments")
        print ("[8]: Get video's METADATA, CHANNELS (creators) for all videos in a PLAYLIST")
        print ("[9]: Get video's COMMENTS and CHANNELS (commenters) for all videos in a PLAYLIST")
        print ("[X]: Exit")

        option = input ("Please introduce your option: ")

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
            get_playlist_comments(youtube,playlist)


        if option == "3":
            ch_id = input("Introduce channel id: ")
            channel_ids = [ch_id]
            get_channels_metadata(youtube, channel_ids, True)


        if option == "4":
            channel_id = input("Introduce channel id: ")
            get_channel_videos_metadata(youtube, channel_id)


        if option == "5":
            query = input("Enter your keyword search: ")
            get_videos_by_keyword_metadata(youtube, query)


        if option=="6":
            video_id = input ("Introduce video id: ")
            get_video_metadata(youtube, video_id)


        if option=="7":
            video_id = input ("Introduce video id: ")
            records = get_video_comments(youtube, video_id, None)
            export_dict_to_excel(records, 'output', 'video_' + video_id + '_comments.xlsx')
            print ("Output is in " + 'video_' + video_id + '_comments.xlsx')


        #Get videos and channels metadata
        if option == "8":
            playlist = get_url_playlist()
            get_playlist_video_and_channels_metadata(youtube, playlist)


        # Get videos and channels metadata
        if option == "9":
            playlist = get_url_playlist()
            get_playlist_comments_and_channels_metadata(youtube, playlist)



        #To get channel metadata for a list of channels
        #channel_ids = ["UCfz0X0J88di_4xIQHf-BI1Q"]
        #get_channels_metadata(youtube, channel_ids, True)












