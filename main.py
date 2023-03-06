from services import *
import sys
import argparse
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
from utils import get_api_key
import state

OUT_OF_QUOTE_MSG = "Quota limit has been reached for today. Please restart the app tomorrow."
STATE_IN_USE_MSG = "There are retrieving actions in queue. Please restart the app tomorrow."




def get_input_arguments():
    my_parser = argparse.ArgumentParser(description='YouTube API scrapper')

    my_parser.add_argument('-o',
                           '--option',
                           action='store',
                           help='YouTube API Menu Option (1, 2, 3, 4, 5)')

    my_parser.add_argument('-p',
                           '--playlist',
                           action='store',
                           help='Playlist to retrieve (for options: 1, 2, or 3)')

    my_parser.add_argument('-q',
                           '--query',
                           action='store',
                           help='Query to search (for options: 4 or 5)')

    my_parser.add_argument('-v',
                           '--videos',
                           action='store',
                           help='Number of videos to search (for options: 4 or 5)')

    my_parser.add_argument('-f',
                           '--filename',
                           action='store',
                           help='Filename (for options: 6, 7, 9, 10, 11)')

    my_parser.add_argument('-a',
                           '--admin',
                           action='store',
                           help='Admin Menu')

    # Execute the parse_args() method
    args = my_parser.parse_args()
    option = args.option
    playlist = args.playlist
    query = args.query
    videos = args.videos
    filename = args.filename
    admin = args.admin

    return option, playlist, query, videos, filename, admin


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
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

    print ("Retrieving info for playlist: " + playlist_title)
    confirm =  input("[Y/N] ")
    if confirm.upper() == "N":
        sys.exit()

    return playlist, playlist_title


#-----------------------------------------------------------------------------------------------------------------------
#This function displays the main menu
#-----------------------------------------------------------------------------------------------------------------------
def display_menu():
    print('\n-------------------- Options --------------------\n')

    #print("[1]: PLAYLIST: Videos")
    #print("[2]: PLAYLIST: Videos' Comments")
    print("[1]: PLAYLIST: Videos and Creators - $")
    print("[2]: PLAYLIST: Videos Comments and Commenters - $$")
    print("[3]: PLAYLIST: Network - $$")
    print("---------------------------------------------------")
    print("[4]: SEARCH: Videos and Creators - $$$")
    print("[5]: SEARCH: Network - $$$$")
    print("---------------------------------------------------")
    print("[6]: FILE: Videos and Creators - $")
    print("[7]: FILE: Comments and Commenters - $$")
    print("[8]: FILE: Network ")
    print("---------------------------------------------------")
    print("[9]: CHANNEL: Metadata - $$")
    print("[10]: CHANNEL: All Videos - $$$$$$")
    print("[11]: CHANNEL: Latest Activity - $$")
    print("---------------------------------------------------")
    print("[12] Compare video's retrieval")
    print("[13] Compare comments' retrieval")
    print("---------------------------------------------------")
    print("[14] Print Quota Usage")
    print("---------------------------------------------------")
    print("[X]: Exit")

    option = input("Please introduce your option: ")

    if not option:
        print('An option should be provided.')
        sys.exit()

    return option


#-----------------------------------------------------------------------------------------------------------------------
#This function displays the main menu
#-----------------------------------------------------------------------------------------------------------------------
def display_restricted_menu():
    print('\n-------------------- Options --------------------\n')

    print("[1] Print Quota Usage")
    print("[2] Print State")
    print("[3] Reset State")
    print("---------------------------------------------------")
    print("[X]: Exit")

    option = input("Please introduce your option: ")

    if not option:
        print('An option should be provided.')
        sys.exit()

    return option



#-----------------------------------------------------------------------------------------------------------------------
#This function executes the option menu interactively
#-----------------------------------------------------------------------------------------------------------------------
def execute_option_restricted(option):

    if option == "1":
        state.print_quote_usage()
        return

    if option == "2":
        state.print_state(state.state_yt)
        return


    if option == "3":
        print ("This option will remove any retrieving actions that are in queue.")
        quote_str = input  ("New quota usage (optional): ")
        try:
            quote = int(quote_str)
        except:
            quote = 0

        proceed = input('Are you sure to proceed? [Y/N] ')
        if proceed.upper() != "Y":
            sys.exit()

        state.state_yt = state.clear_state(state.state_yt, clear_quote=True, clear_api_key=False)
        state.state_yt = state.set_quote_usage(state.state_yt, quote)

    sys.exit()


#-----------------------------------------------------------------------------------------------------------------------
#This function executes the option menu interactively
#-----------------------------------------------------------------------------------------------------------------------
def execute_option_interactive(option):
    # Playlists options
    if option == "1" or option == "2" or option == "3":
        playlist, playlist_title = get_playlist_info()

    # Get all videos' metadata from playlist in config.
    #if option == "1":
    #    get_playlist_metadata(youtube, playlist, playlist_title)
    #    return

    # Get all comments for all the videos on a playlist
    #if option == "2":
    #    get_playlist_videos_comments(youtube, playlist, playlist_title)
    #    return

    # Get videos and creators
    if option == "1":
        get_playlist_videos_and_videocreators(youtube, playlist, playlist_title)
        return

    # Get comments and commenters
    if option == "2":
        get_playlist_videocomments_and_commenters(youtube, playlist, playlist_title)
        return

    # Build a network for a playlist
    if option == "3":
        get_playlist_network(youtube, playlist, playlist_title)
        return

    if option == "4":
        # query = get_query()
        query = input("Please introduce the query to search: ")
        if len(query) == 0:
            print("Invalid query")
            sys.exit()

        max_videos_with_quote = state.number_of_items_with_quote(state.UNITS_SEARCH_LIST,
                                                                 state.MAX_SEARCH_RESULTS_PER_REQUEST)

        print ("Maximum videos to search is: {}".format(max_videos_with_quote))
        numberVideos_str = input("Enter number of videos to search (optional, default is {}): ".format(state.DEFAULT_VIDEOS_TO_RETRIEVE))
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=None)
        return

    if option == "5":
        # query = get_query()
        query = input("Please introduce the query to search: ")
        if len(query) == 0:
            print("Invalid query")
            sys.exit()

        max_videos_with_quote = state.number_of_items_with_quote(state.UNITS_SEARCH_LIST,
                                                                 state.MAX_SEARCH_RESULTS_PER_REQUEST)

        print ("Maximum videos to retrieve with available quota is: {}".format(max_videos_with_quote))
        numberVideos_str = input("Enter number of videos to retrieve (optional, default is {}): ".format(state.DEFAULT_VIDEOS_TO_RETRIEVE))
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=True)
        return

    if option == "6":
        filename = input("Filename with videos Ids to request videos and creators: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        get_videos_and_videocreators_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "7":
        filename = input("Filename with videos Ids to request comments and commenters: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        get_videos_comments_and_commenters_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "8":
        videosFilename = input("Filename with videos and creators: ")
        commentsFilename = input("Filename with comments and commenters: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        output_file = export_network_file("from_file_" + prefix, videosFilename=videosFilename.rstrip(),
                                          commentsFilename=commentsFilename.rstrip())
        print("Output is in :" + output_file)
        return

    if option == "9":
        file = input("Input file with channels ids to retrieve channel's metadata: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_metadata_channels_from_file(youtube, file.rstrip(), prefix)
        return

    if option == "10":
        file = input("Input file with channels ids to retrieve all videos: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_all_videos_by_all_channels_from_file(youtube, file.rstrip(), prefix)
        return

    if option == "11":
        file = input("Input file with channels ids to retrieve the latest channels' activity: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_channels_activity_from_file(youtube, file.rstrip(), prefix)
        return

    if option == "12":
        file1 = input("1st. File to compare (videos & creators): ")
        file2 = input("2nd. File to compare (videos & creators): ")
        filename = input("Type an infix  for the output filename [optional]: ")
        compare_video_creators_files(file1.rstrip(), file2.rstrip(), filename)
        return

    if option == "13":
        file1 = input("1st. File to compare (comments & commenters): ")
        file2 = input("2nd. File to compare (comments & commenters): ")
        filename = input("Type an infix  for the output filename [optional]: ")
        compare_comments_commenters_files(file1.rstrip(), file2.rstrip(), filename)
        return

    if option == "14":
        state.print_quote_usage()
        return


    #if option == "15":
    #    print ("This option will remove any retrieving actions that are in queue.")
    #    quote_str = input  ("Quote usage (optional): ")
    #    try:
    #        quote = int(quote_str)
    #    except:
    #        quote = 0
    #
    #    proceed = input('Are you sure to proceed? [Y/N]')
    #    if proceed.upper() != "Y":
    #        sys.exit()

        state.state_yt = state.clear_state(state.state_yt, clear_quote=True, clear_api_key=False)
        state.state_yt = state.set_quote_usage(state.state_yt, quote)


#-----------------------------------------------------------------------------------------------------------------------
#This function executes the option menu without user intervention
#-----------------------------------------------------------------------------------------------------------------------
def execute_option(option, playlist, query, videos, filename):

    prefix=""
    if option == "1" or option == "2" or option == "3":
        url = playlist
        url = url.strip()
        if not url:
            print("Invalid URL")
            sys.exit()

        playlist = get_playlist_id(url)
        if not playlist:
            print ("Invalid URL")
            sys.exit()

        playlist_title = get_playlist_title(youtube, playlist)
        if not playlist_title:
            print("The URL doesn't correspond to a playlist.")
            sys.exit()

    # Get videos and creators
    if option == "1":
        get_playlist_videos_and_videocreators(youtube, playlist, playlist_title)
        return

    # Get comments and commenters
    if option == "2":
        get_playlist_videocomments_and_commenters(youtube, playlist, playlist_title)
        return

    # Build a network for a playlist
    if option == "3":
        get_playlist_network(youtube, playlist, playlist_title)
        return

    if option == "4":
        if len(query) == 0:
            print("Invalid query")
            sys.exit()
        numberVideos_str = videos
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=None, interactive=False)
        return

    if option == "5":
        if len(query) == 0:
            print("Invalid query")
            sys.exit()

        numberVideos_str = videos
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=True, interactive=False)
        return

    if option == "6":
        get_videos_and_videocreators_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "7":
        get_videos_comments_and_commenters_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "9":
        get_metadata_channels_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "10":
        get_all_videos_by_all_channels_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "11":
        get_channels_activity_from_file(youtube, filename.rstrip(), prefix)
        return


#-----------------------------------------------------------------------------------------------------------------------
#This function gets the state on file (quote usage and others)
#If there is no state on file, the app hasn't been used for the day and the quote is initialized to zero
#Add api_key --->REVISIT THIS!
#-----------------------------------------------------------------------------------------------------------------------
def initialize_quote():
    state_on_file = state.load_state_from_file()
    if state_on_file:
        state.state_yt = state_on_file
    else:
        state.state_yt  = state.set_api_key(state.state_yt, get_api_key())


#-----------------------------------------------------------------------------------------------------------------------
#Reset the state after
#-----------------------------------------------------------------------------------------------------------------------
def reset_state(clear_quote=False, clear_api_key=False):

    if len(state.state_yt[state.LIST_ACTIONS])==0:
        state.state_yt = state.clear_state(state.state_yt, clear_quote, clear_api_key)

    if (len(state.state_yt[state.LIST_ACTIONS])>0 and len(state.state_yt[state.VIDEOS_IDS_FILE])==0
            and len(state.state_yt[state.CHANNELS_IDS_FILE])==0):
        #Something went wrong.
        #There actions to retrieve but not videos' id or channels' ids where to take the ids.
        state.state_yt = state.clear_state(state.state_yt, clear_quote, clear_api_key)


#-----------------------------------------------------------------------------------------------------------------------
#This function prints a msg when the quote capacity has been reached and exits the program
#-----------------------------------------------------------------------------------------------------------------------
def check_out_of_quote():
    #We verify if we can perform any other request
    if len(state.state_yt[state.LIST_ACTIONS])>0:
        print(STATE_IN_USE_MSG)
        sys.exit()

    if not state.continue_to_retrieve(state.state_yt):
        print(OUT_OF_QUOTE_MSG)
        sys.exit()


#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    initialize_quote()
    #state.state_yt = state.set_quote_usage(state.state_yt,1097)
    #state.print_state(state.state_yt)
    state.print_quote_usage()

    # Get input arguments to run options without user intervention
    option, playlist, query, videos, filename, admin = get_input_arguments()

    if admin:
        option = display_restricted_menu()
        execute_option_restricted(option)
        sys.exit()

    #Check quote usage
    check_out_of_quote()

    youtube = build_service_api_key()
    if not youtube:
        print("Error when creating API Youtube service.")
        sys.exit()


    if option:
        execute_option(option, playlist, query, videos, filename)
        check_out_of_quote()
        reset_state()
    else:
        option = ""
        while (option.upper() != "X"):
            option = display_menu()
            execute_option_interactive(option)
            check_out_of_quote()
            # If there is enough quote usage, the state should be cleared for the following option as options are independent
            reset_state()
            state.print_quote_usage()
            option ="X"
            if option.upper() != "X":
                input("Press any key to continue")

    #state.print_state(state.state_yt)












