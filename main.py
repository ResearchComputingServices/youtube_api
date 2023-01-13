from services import *
import sys
from playlists import get_playlist_metadata
from playlists import get_playlist_videos_comments
from playlists import get_playlist_videos_and_videocreators
from playlists import get_playlist_videocomments_and_commenters
from playlists import get_playlist_network
from playlists import get_playlist_title
from channels import get_all_videos_by_all_channels_from_file
from channels import get_metadata_channels_from_file
from channels import get_videos_and_videocreators_from_file
from channels import get_channels_activity_from_file
from comments import get_videos_comments_and_commenters_from_file
from search import search_videos_youtube
from network import export_network_file
from compare import compare_video_creators_files
from compare import compare_comments_commenters_files
from utils import get_playlist_id



def get_playlist_info():
    url = input("Enter URL of the playlist to retrieve videos: ")
    url = url.strip()
    if not url:
        print("Invalid URL")
        sys.exit()

    playlist = get_playlist_id(url)
    if not playlist:
        sys.exit()

    playlist_title = get_playlist_title(youtube, playlist)
    if not playlist_title:
        print ("The URL doesn't correspond to a playlist.")
        sys.exit()

    print ("Retrieving videos for playlist: " + playlist_title)
    confirm =  input("[Y/N] ")
    if confirm.upper() == "N":
        sys.exit()

    return playlist, playlist_title


def display_menu():
    print('\n-------------------- Options --------------------\n')

    print("[1]: PLAYLIST: Videos")
    print("[2]: PLAYLIST: Videos' Comments")
    print("[3]: PLAYLIST: Videos and Creators")
    print("[4]: PLAYLIST: Videos Comments and Commenters")
    print("[5]: PLAYLIST: Network")
    print("---------------------------------------------------")
    print("[6]: SEARCH: Videos and Creators")
    print("[7]: SEARCH: Network")
    print("---------------------------------------------------")
    print("[8]: FILE: Videos and Creators")
    print("[9]: FILE: Comments and Commenters")
    print("[10]: FILE: Network")
    print("---------------------------------------------------")
    print("[11]: CHANNEL: Metadata")
    print("[12]: CHANNEL: All Videos")
    print("[13]: CHANNEL: Latest Activity")
    print("---------------------------------------------------")
    print("[14] Compare video's retrieval")
    print("[15] Compare comments' retrieval")
    print("---------------------------------------------------")
    print("[X]: Exit")

    option = input("Please introduce your option: ")

    if not option:
        print('An option should be provided.')
        sys.exit()

    return option


def execute_option(option):
    # Playlists options
    if option == "1" or option == "2" or option == "3" or option == "4" or option == "5":
        playlist, playlist_title = get_playlist_info()

    # Get all videos' metadata from playlist in config.
    if option == "1":
        get_playlist_metadata(youtube, playlist, playlist_title)

    # Get all comments for all the videos on a playlist
    if option == "2":
        get_playlist_videos_comments(youtube, playlist, playlist_title)

    # Get videos and creators
    if option == "3":
        get_playlist_videos_and_videocreators(youtube, playlist, playlist_title)

    # Get comments and commenters
    if option == "4":
        get_playlist_videocomments_and_commenters(youtube, playlist, playlist_title)

    # Build a network for a playlist
    if option == "5":
        get_playlist_network(youtube, playlist, playlist_title)

    if option == "6":
        # query = get_query()
        query = input("Please introduce the query to search: ")
        if len(query) == 0:
            print("Invalid query")
            sys.exit()
        numberVideos_str = input("Enter maximum number of videos to retrieve (optional): ")
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=None)

    if option == "7":
        # query = get_query()
        query = input("Please introduce the query to search: ")
        if len(query) == 0:
            print("Invalid query")
            sys.exit()

        numberVideos_str = input("Enter a maximum number of videos to retrieve (optional): ")
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=True)

    if option == "8":
        filename = input("Filename with videos Ids to request videos and creators: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        get_videos_and_videocreators_from_file(youtube, filename.rstrip(), prefix)

    if option == "9":
        filename = input("Filename with videos Ids to request comments and commenters: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        get_videos_comments_and_commenters_from_file(youtube, filename.rstrip(), prefix)

    if option == "10":
        videosFilename = input("Filename with videos and creators: ")
        commentsFilename = input("Filename with comments and commenters: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        output_file = export_network_file("from_file_" + prefix, videosFilename=videosFilename.rstrip(),
                                          commentsFilename=commentsFilename.rstrip())
        print("Output is in :" + output_file)

    if option == "11":
        file = input("Input file with channels ids to retrieve channel's metadata: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_metadata_channels_from_file(youtube, file.rstrip(), prefix)

    if option == "12":
        file = input("Input file with channels ids to retrieve all videos: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_all_videos_by_all_channels_from_file(youtube, file.rstrip(), prefix)

    if option == "13":
        file = input("Input file with channels ids to retrieve the latest channels' activity: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_channels_activity_from_file(youtube, file.rstrip(), prefix)

    # if option=="14":
    #    video_id = input ("Introduce video id: ")
    #    get_video_metadata(youtube, video_id)

    # if option=="15":
    #    video_id = input ("Introduce video id: ")
    #    records = get_video_comments(youtube, video_id, None)
    #    filename = export_dict_to_excel(records, 'output', 'video_' + video_id + '_comments.xlsx')
    #    print ("Output is in: " + 'video_' + video_id + '_comments.xlsx')

    if option == "14":
        file1 = input("1st. File to compare (videos & creators): ")
        file2 = input("2nd. File to compare (videos & creators): ")
        filename = input("Type an infix  for the output filename [optional]: ")
        compare_video_creators_files(file1.rstrip(), file2.rstrip(), filename)

    if option == "15":
        file1 = input("1st. File to compare (comments & commenters): ")
        file2 = input("2nd. File to compare (comments & commenters): ")
        filename = input("Type an infix  for the output filename [optional]: ")
        compare_comments_commenters_files(file1.rstrip(), file2.rstrip(), filename)


if __name__ == "__main__":

    option=""
    #youtube = build_service_oauth()
    youtube = build_service_api_key()

    if not youtube:
        print("Error when creating API Youtube service.")
        sys.exit()

    # Retrieves the title of the playlist
    #playlist = get_url_playlist()
    #if not playlist:
    #    sys.exit()
    #playlist_title = get_playlist_title(youtube, playlist)

    while (option.upper()!="X"):
        option = display_menu()
        execute_option(option)
        if option.upper()!="X":
            input("Press any key to continue")












