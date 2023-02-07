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
from utils import get_api_key
import state
from utils import remove_prefix_url


OUT_OF_QUOTE_MSG = "Quote limit has been reached for today. Please restart the app tomorrow."
STATE_IN_USE_MSG = "There are retrieving actions in queue. Please restart the app tomorrow."

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
    print("[16] Print Quote Usage")
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
        return

    # Get all comments for all the videos on a playlist
    if option == "2":
        get_playlist_videos_comments(youtube, playlist, playlist_title)
        return

    # Get videos and creators
    if option == "3":
        get_playlist_videos_and_videocreators(youtube, playlist, playlist_title)
        return

    # Get comments and commenters
    if option == "4":
        get_playlist_videocomments_and_commenters(youtube, playlist, playlist_title)
        return

    # Build a network for a playlist
    if option == "5":
        get_playlist_network(youtube, playlist, playlist_title)
        return

    if option == "6":
        # query = get_query()
        query = input("Please introduce the query to search: ")
        if len(query) == 0:
            print("Invalid query")
            sys.exit()

        max_videos_with_quote = state.number_of_items_with_quote(state.UNITS_SEARCH_LIST,
                                                                 state.MAX_SEARCH_RESULTS_PER_REQUEST)

        print ("Maximum videos to search with available quote is: {}".format(max_videos_with_quote))
        numberVideos_str = input("Enter number of videos to search (optional, default is {}): ".format(state.DEFAULT_VIDEOS_TO_RETRIEVE))
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=None)
        return

    if option == "7":
        # query = get_query()
        query = input("Please introduce the query to search: ")
        if len(query) == 0:
            print("Invalid query")
            sys.exit()

        max_videos_with_quote = state.number_of_items_with_quote(state.UNITS_SEARCH_LIST,
                                                                 state.MAX_SEARCH_RESULTS_PER_REQUEST)

        print ("Maximum videos to retrieve with available quote is: {}".format(max_videos_with_quote))
        numberVideos_str = input("Enter number of videos to retrieve (optional, default is {}): ".format(state.DEFAULT_VIDEOS_TO_RETRIEVE))
        try:
            numberVideos = int(numberVideos_str)
        except:
            numberVideos = None
        search_videos_youtube(youtube, query, maxNumberVideos=numberVideos, network=True)
        return

    if option == "8":
        filename = input("Filename with videos Ids to request videos and creators: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        get_videos_and_videocreators_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "9":
        filename = input("Filename with videos Ids to request comments and commenters: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        get_videos_comments_and_commenters_from_file(youtube, filename.rstrip(), prefix)
        return

    if option == "10":
        videosFilename = input("Filename with videos and creators: ")
        commentsFilename = input("Filename with comments and commenters: ")
        prefix = input("Type a prefix for the output filename [optional]: ")
        output_file = export_network_file("from_file_" + prefix, videosFilename=videosFilename.rstrip(),
                                          commentsFilename=commentsFilename.rstrip())
        print("Output is in :" + output_file)
        return

    if option == "11":
        file = input("Input file with channels ids to retrieve channel's metadata: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_metadata_channels_from_file(youtube, file.rstrip(), prefix)
        return

    if option == "12":
        file = input("Input file with channels ids to retrieve all videos: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_all_videos_by_all_channels_from_file(youtube, file.rstrip(), prefix)
        return

    if option == "13":
        file = input("Input file with channels ids to retrieve the latest channels' activity: ")
        prefix = input("Introduce a prefix name for the file: ")
        get_channels_activity_from_file(youtube, file.rstrip(), prefix)
        return

    # if option=="14":
    #    video_id = input ("Introduce video id: ")
    #    get_video_metadata(youtube, video_id)
    #   return

    # if option=="15":
    #    video_id = input ("Introduce video id: ")
    #    records = get_video_comments(youtube, video_id, None)
    #    filename = export_dict_to_excel(records, 'output', 'video_' + video_id + '_comments.xlsx')
    #    print ("Output is in: " + 'video_' + video_id + '_comments.xlsx')
    #   return

    if option == "14":
        file1 = input("1st. File to compare (videos & creators): ")
        file2 = input("2nd. File to compare (videos & creators): ")
        filename = input("Type an infix  for the output filename [optional]: ")
        compare_video_creators_files(file1.rstrip(), file2.rstrip(), filename)
        return

    if option == "15":
        file1 = input("1st. File to compare (comments & commenters): ")
        file2 = input("2nd. File to compare (comments & commenters): ")
        filename = input("Type an infix  for the output filename [optional]: ")
        compare_comments_commenters_files(file1.rstrip(), file2.rstrip(), filename)
        return

    if option == "16":
        state.print_quote_usage()
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
        state.set_api_key(state.state_yt, get_api_key())

#-----------------------------------------------------------------------------------------------------------------------
#Reset the state after
#-----------------------------------------------------------------------------------------------------------------------
def reset_state(clear_quote=False, clear_api_key=False):
    if len(state.state_yt[state.LIST_ACTIONS])==0:
        #There is still at least one action that couldn't be completed.
        state.state_yt = state.clear_state(state.state_yt, clear_quote, clear_api_key)

    if len(state.state_yt[state.LIST_ACTIONS])>0 and len(state.state_yt[state.VIDEOS_IDS_FILE])==0:
        #Something went wrong.
        #There actions to retrieve but not videos' id file where to take the ids.
        state.state_yt = state.clear_state(state.state_yt, clear_quote, clear_api_key)


#-----------------------------------------------------------------------------------------------------------------------
#This function prints a msg when the quote capacity has been reached and exits the program
#-----------------------------------------------------------------------------------------------------------------------
def out_of_quote_msg():
    #We verify if we can perform any other request
    if len(state.state_yt[state.LIST_ACTIONS])>0:
        print(STATE_IN_USE_MSG)
        sys.exit()

    if not state.continue_to_retrieve(state.state_yt):
        print(OUT_OF_QUOTE_MSG)
        sys.exit()


#-----------------------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    #url = "https://yt3.ggpht.com/ytc/AL5GRJW_GP6jGD-L9YLvDrixKZSsmXh-oNnfOBwmD8Kc9A=s48-c-k-c0x00ffffff-no-rj"
    #url = 'http://www.youtube.com/channel/UCSIN1AD8IFbr7II4eZFbhdQ'
    #link = remove_prefix_url(url)
    
    #print (link)

    # Get the current quote
    #state.update_quote_usage(state.state_yt,1945)
    #state.state_yt = state.load_state_from_file()
    #state.clear_state(state.state_yt)  # Quote usage remains and it will not be cleared out
    initialize_quote()
    state.print_state(state.state_yt)
    state.print_quote_usage()
    out_of_quote_msg()

    #out_of_quote_msg()
    #state.print_quote_usage()

    option = ""
    # youtube = build_service_oauth()
    youtube = build_service_api_key()
    if not youtube:
        print("Error when creating API Youtube service.")
        sys.exit()


    while (option.upper() != "X"):
        option = display_menu()
        execute_option(option)
        out_of_quote_msg()
        # If there is enough quote usage, the state should be cleared for the following option as options are independent
        reset_state()
        state.print_quote_usage()
        if option.upper() != "X":
            input("Press any key to continue")

    state.print_state(state.state_yt)












