from services import *
import sys
from playlists import get_playlist_metadata
from playlists import get_playlist_videos_comments
from playlists import get_playlist_videos_and_videocreators
from playlists import get_playlist_videocomments_and_commenters
from playlists import get_playlist_network
from playlists import get_playlist_title
from channels import get_all_videos_by_a_channel
from channels import get_channels_metadata
from channels import get_videos_and_videocreators_from_file
from videos import get_video_metadata
from comments import get_video_comments
from comments import get_videos_comments_and_commenters_from_file
from search import search_videos_youtube
from network import export_network_file



if __name__ == "__main__":

    option=""
    #youtube = build_service_oauth()

    youtube = build_service_api_key()

    if not youtube:
        print("Error when creating API Youtube service.")
        sys.exit()

    #Retrieves the title of the playlist
    playlist = get_url_playlist()
    playlist_title = get_playlist_title(youtube, playlist)

    while (option.upper()!="X"):
        print ('\n-------------------- Options --------------------\n')

        print ("[1]: PLAYLIST: Videos")
        print ("[2]: PLAYLIST: Videos' Comments")
        print ("[3]: PLAYLIST: Videos and Creators)")
        print ("[4]: PLAYLIST: Videos Comments and Commenters")
        print ("[5]: PLAYLIST: Network")
        print ("---------------------------------------------------")
        print ("[6]: SEARCH: Videos and Creators")
        print ("[7]: SEARCH: Network")
        print("---------------------------------------------------")
        print ("[8]: FILE: Videos and Creators")
        print ("[9]: FILE: Comments and Commenters")
        print ("[10]: FILE: Network")
        print("---------------------------------------------------")
        print ("[11]: CHANNEL: Metadata")
        print ("[12]: CHANNEL: Videos")
        print("---------------------------------------------------")
        print ("[13]: VIDEO: Metadata and Creator")
        print ("[14]: VIDEO: Comments and Commenters")
        print("---------------------------------------------------")
        print ("[X]: Exit")

        option = input ("Please introduce your option: ")
        #option="10"

        if not option:
            print('An option should be provided.')
            sys.exit()

        #Get all videos' metadata from playlist in config.
        if option == "1":
            get_playlist_metadata(youtube, playlist,playlist_title)


        #Get all comments for all the videos on a playlist
        if option  == "2":
            get_playlist_videos_comments(youtube, playlist, playlist_title)


        #Get videos and creators
        if option == "3":
            get_playlist_videos_and_videocreators(youtube, playlist, playlist_title)


        # Get comments and commenters
        if option == "4":
            get_playlist_videocomments_and_commenters(youtube, playlist, playlist_title)

        #Build a network for a playlist
        if option == "5":
            get_playlist_network(youtube, playlist,playlist_title)

        if option == "6":
            query = get_query()
            #search_videos_youtube(youtube, query, maxNumberVideos=5)
            search_videos_youtube(youtube, query, maxNumberVideos=None, network=None)

        if option == "7":
            query = get_query()
            #search_videos_youtube(youtube, query, maxNumberVideos =10, network=True)
            search_videos_youtube(youtube, query, network=True)

        if option == "8":
            filename = input ("Filename with videos Ids to request (videos and creators): ")
            prefix =  input ("Type a prefix for the output filename [optional]: ")
            get_videos_and_videocreators_from_file(youtube, filename, prefix)

        if option == "9":
            filename = input ("Filename with videos Ids to request (comments and commenters): ")
            prefix = input("Type a prefix for the output filename [optional]: ")
            get_videos_comments_and_commenters_from_file(youtube, filename, prefix)

        if option == "10":
            videosFilename = input ("Filename with videos and creators: ")
            commentsFilename = input ("Filename with comments and commenters: ")
            prefix = input("Type a prefix for the output filename [optional]: ")
            output_file = export_network_file("from_file_" + prefix , videosFilename=videosFilename,
                                              commentsFilename=commentsFilename)
            print("Output is in :" + output_file)

        if option == "11":
            ch_id = input("Introduce channel id: ")
            channel_ids = [ch_id]
            get_channels_metadata(youtube, channel_ids, True)

        if option == "12":
            channel_id = input("Introduce channel id: ")
            get_all_videos_by_a_channel(youtube, channel_id)

        if option=="13":
            video_id = input ("Introduce video id: ")
            get_video_metadata(youtube, video_id)


        if option=="14":
            video_id = input ("Introduce video id: ")
            records = get_video_comments(youtube, video_id, None)
            filename = export_dict_to_excel(records, 'output', 'video_' + video_id + '_comments.xlsx')
            print ("Output is in: " + 'video_' + video_id + '_comments.xlsx')



        #option = "x"
        #if option=="11":
        #    export_network_file_2()

        #if option=="12":
        #    demo()
        #    option = "x"

        #To get channel metadata for a list of channels
        #channel_ids = ["UCfz0X0J88di_4xIQHf-BI1Q"]
        #get_channels_metadata(youtube, channel_ids, True)












