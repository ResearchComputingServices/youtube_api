import state
import pandas as pd
import shutil
from channels import get_videos_and_videocreators_from_file
from channels import get_metadata_channels_from_file
from channels import get_all_videos_by_all_channels_from_file
from channels import get_channels_activity_from_file
from comments import get_videos_comments_and_commenters_from_file
from services import build_service_api_key
from utils import get_filename
from utils import export_dataframe_to_excel
from utils import export_dict_to_csv
from utils import get_fullpath
from network import export_network_file
from datetime import datetime
from utils import get_api_key
import traceback
import sys


OUTPUT_DIRECTORY = "output"
OUTPUT_VIDEOS_FILE_NAME = "merged_videos_creators"
OUTPUT_COMMENTS_FILE_NAME = "merged_comments_commenters"
OUTPUT_SUB_COMMENTS_FILE_NAME = "merged_subcomments"
OUTPUT_CHANNEL_METADATA_FILE_NAME = "merged_channels_metadata"
OUTPUT_CHANNEL_ACTIVITY_FILE_NAME = "merged_channels_activity"
OUTPUT_CHANNEL_ALL_VIDEOS_FILE_NAME = "merged_channels_all_videos"
CHANNEL_METADATA_TEXT = "Metadata for all the channels"
CHANNEL_ACTIVITY_TEXT = "Last activity for all the channels"
CHANNEL_ALL_VIDEOS_TEXT = "All the videos for all the channels"

EXTENSION = "xlsx"
MSG_LIST = []



#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def merge_csv_files(file_list,output_filename):

    filename_path = ""
    try:
        if len(file_list)>0:
            filename = file_list[0]
            dataF = pd.read_csv(filename).T

            i = 1
            while (i < len(file_list)):
                filename = file_list[i]
                data = pd.read_csv(filename).T
                dataF = pd.concat([dataF, data], axis=1, ignore_index=True)
                i = i + 1

            date_name = get_filename(output_filename, EXTENSION)
            filename_path = export_dict_to_csv(dataF,OUTPUT_DIRECTORY,date_name)
    except:
        print ("Error when merging CSV files")
        print(sys.exc_info()[0])
        traceback.print_exc()
        filename_path = "-1"

    return filename_path


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def merge_excel_files(file_list, output_filename):

    filename_path = ""
    try:
        if len(file_list)>0:
            filename = file_list[0]
            dataF = pd.read_excel(filename).T

            i = 1
            while (i < len(file_list)):
                filename = file_list[i]
                data = pd.read_excel(filename).T
                dataF = pd.concat([dataF, data], axis=1, ignore_index=True)
                i = i + 1

            date_name = get_filename(output_filename, EXTENSION)
            filename_path = export_dataframe_to_excel(dataF,OUTPUT_DIRECTORY,date_name)
    except:
        print ("Error when merging excel files")
        print(sys.exc_info()[0])
        traceback.print_exc()
        filename_path = "-1"
    return filename_path


#-----------------------------------------------------------------------------------------------------------------------
#Reset the quote to zero
#-----------------------------------------------------------------------------------------------------------------------
def reset_quote():
    state_on_file = state.load_state_from_file()
    if state_on_file:
        state.state_yt = state_on_file
    else:
        state.state_yt = state.set_api_key(state.state_yt, get_api_key())

    state.state_yt = state.set_quote_usage(state.state_yt, 0)
    #state.print_state(state.state_yt)


#-----------------------------------------------------------------------------------------------------------------------
#This function will resume the retrieval of channel's metadata for a set of channels ids
#Starting in a particular index
#-----------------------------------------------------------------------------------------------------------------------
def resume_channels_metadata_retrievals(youtube, state_pr):
    print ("Resuming channel's metadata retrievals...\n")
    #Get filename with the videos ids to request
    filename = state_pr[state.CHANNELS_IDS_FILE]
    start_index = state_pr[state.CHANNEL_INDEX]
    prefix = "state"
    get_metadata_channels_from_file(youtube, filename, prefix, start_index)


#-----------------------------------------------------------------------------------------------------------------------
#This function will resume the retrieval of all videos by a channel for a set of channels ids
#Starting in a particular index
#-----------------------------------------------------------------------------------------------------------------------
def resume_channels_all_videos_retrievals(youtube, state_pr):
    print ("Resuming all videos by a channel retrievals...\n")
    #Get filename with the videos ids to request
    filename = state_pr[state.CHANNELS_IDS_FILE]
    start_index = state_pr[state.CHANNEL_INDEX]
    prefix = "state"
    get_all_videos_by_all_channels_from_file(youtube, filename, prefix, start_index)

#-----------------------------------------------------------------------------------------------------------------------
#This function will resume the retrieval of all videos by a channel for a set of channels ids
#Starting in a particular index
#-----------------------------------------------------------------------------------------------------------------------
def resume_channels_activity_retrievals(youtube, state_pr):
    print ("Resuming latest activity for a list of channels... \n")
    filename = state_pr[state.CHANNELS_IDS_FILE]
    start_index = state_pr[state.CHANNEL_INDEX]
    prefix = "state"
    get_channels_activity_from_file(youtube, filename, prefix, start_index)


#-----------------------------------------------------------------------------------------------------------------------
#This function will resume the retrieval of videos for a set of videos ids
#Starting in a particular index
#-----------------------------------------------------------------------------------------------------------------------
def resume_video_retrievals(youtube, state_pr):
    print ("Resuming video retrievals...\n")
    #Get filename with the videos ids to request
    filename = state_pr[state.VIDEOS_IDS_FILE]
    start_index = state_pr[state.VIDEO_INDEX]
    prefix = "state"
    get_videos_and_videocreators_from_file(youtube, filename, prefix, start_index)



#-----------------------------------------------------------------------------------------------------------------------
#This function will resume the retrieval of comments for a set of videos ids
#Starting in a particular index
#-----------------------------------------------------------------------------------------------------------------------
def resume_comments_retrievals(youtube, state_pr):
    # Get filename with the videos ids to request
    print ("Resuming comments retrievals...\n")
    filename = state_pr[state.VIDEOS_IDS_FILE]
    start_index = state_pr[state.COMMENT_INDEX]
    comments_count_filename = state_pr[state.COMMENTS_COUNT_FILE]
    prefix = "state"
    get_videos_comments_and_commenters_from_file(youtube, filename, prefix, comments_count_filename, start_index)


#-----------------------------------------------------------------------------------------------------------------------
#This function will merge the videos and comments files and create a network from them
#-----------------------------------------------------------------------------------------------------------------------
def output_retrievals():

    print ("Merging files for output...")
    success = True
    try:
        videos_merged_file = merge_excel_files(state.state_yt[state.LIST_VIDEOS_TO_MERGE], OUTPUT_VIDEOS_FILE_NAME)
        state.state_yt[state.VIDEOS_MERGED]= videos_merged_file

        comments_merged_file = merge_excel_files(state.state_yt[state.LIST_COMMENTS_TO_MERGE], OUTPUT_COMMENTS_FILE_NAME)
        #sub_comments_merged_file = merge_csv_files(state.state_yt[state.LIST_SUBCOMMENTS_TO_MERGE], OUTPUT_SUB_COMMENTS_FILE_NAME)
        state.state_yt[state.COMMENTS_MERGED] = comments_merged_file

        if videos_merged_file!="-1" and comments_merged_file!="-1":
            output_file = export_network_file("from_retrievals_", videosFilename=videos_merged_file.rstrip(),commentsFilename=comments_merged_file.rstrip())
            state.state_yt[state.NETWORK_FILE] = output_file
            state.remove_action(state.state_yt,state.ACTION_CREATE_NETWORK)

    except:
        success = False
        print("Error on output_retrievals ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return success

#-----------------------------------------------------------------------------------------------------------------------
#This function will merge channel retrievals
#-----------------------------------------------------------------------------------------------------------------------
def output_channel_retrievals(output_filename):

    print ("Merging files for output...")
    success = True
    try:
        channels_merged_file = merge_excel_files(state.state_yt[state.LIST_CHANNELS_TO_MERGE], output_filename)
        state.state_yt[state. CHANNELS_MERGED]= channels_merged_file
    except:
        success = False
        print("Error on output_channel_retrievals ")
        print(sys.exc_info()[0])
        traceback.print_exc()

    return success

# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
def notify_user_on_file(nothing_to_retrieve=False, success=True):

    try:
        #Open file
        name = get_filename("summary","txt")
        fullname = get_fullpath("summaries", name)
        fullname_plain = get_fullpath("summaries", "summary.txt")
        f = open(fullname,'w+')

        f.write("\n*****************************************************************\n")
        f.write("Retrieving status\n")
        now = datetime.now()
        dt_string = now.strftime("%b %d %Y %H:%M:%S")
        f.write(dt_string)
        f.write("\n")


        if len(state.state_yt["videos_files_to_merge"]) > 0 and (
                state.ACTION_RETRIEVE_VIDEOS not in state.state_yt["actions"]):
            f.write("\n** Sucessive video retrievals are located in: \n")
            for p in state.state_yt["videos_files_to_merge"]:
                f.write(p)
                f.write("\n")

        if len(state.state_yt["videos_merged"]) > 0:
            if state.state_yt["videos_merged"] != "-1":
                f.write("\n** File with merged retrievals' videos are located in: \n")
                f.write(state.state_yt["videos_merged"])
                f.write("\n")
            else:
                f.write("An error occurred when merging retrieved video files. \n")

        if len(state.state_yt["comments_files_to_merge"]) > 0 and (
                state.ACTION_RETRIEVE_COMMENTS not in state.state_yt["actions"]):
            f.write("\n** Sucessive comments retrievals are located in: \n")
            for p in state.state_yt["subcomments_files_to_merge"]:
                f.write(p)
                f.write("\n")

            for p in state.state_yt["comments_files_to_merge"]:
                f.write(p)
                f.write("\n")

        if len(state.state_yt["comments_merged"]) > 0:
            if state.state_yt["comments_merged"] != "-1":
                f.write("\n** File with merged retrievals' comments are located in: \n")
                f.write(state.state_yt["comments_merged"])
                f.write("\n")
            else:
                f.write("An error occurred when merging retrieved comments files. \n")

        if state.state_yt["network_file"]:
            if len(state.state_yt["network_file"]) > 0:
                f.write("\n** Network file is located in: \n")
                f.write(state.state_yt["network_file"])
                f.write("\n")

        f.write("\n")
        if len(state.state_yt["actions"]) == 0:
            if nothing_to_retrieve:
                f.write("** No pending actions to retrieve \n")
            else:
                if success:
                    f.write("** Retrieving completed \n")
                else:
                    f.write("** An error ocurred while retrieving and/or merging files. Please try the request again. \n")
        else:
            f.write("** The following actions will be completed when quote is available: \n")
            if (state.ACTION_RETRIEVE_VIDEOS in state.state_yt["actions"]):
                f.write("Retrieve videos \n")
            if (state.ACTION_RETRIEVE_COMMENTS in state.state_yt["actions"]):
                f.write("Retrieve comments \n")
            if (state.ACTION_CREATE_NETWORK in state.state_yt["actions"]):
                f.write("Build Network \n")
    except:
        f.write ("An error occurred while creating this summary. \n")

    f.close()
    shutil.copyfile(fullname,fullname_plain)

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def notify_user(nothing_to_retrieve=False, success=True):

    print ("\n*******************************************************************************************")
    print ("Retrieving status")
    now = datetime.now()
    dt_string = now.strftime("%b %d %Y %H:%M:%S")
    print(dt_string)


    state.print_quote_usage()

    if len(state.state_yt["videos_files_to_merge"])>0 and (state.ACTION_RETRIEVE_VIDEOS not in state.state_yt["actions"]):
        print ("\n** Sucessive video retrievals are located in: ")
        for f in state.state_yt["videos_files_to_merge"]:
            print (f)

    if len(state.state_yt["videos_merged"])>0:
        if state.state_yt["videos_merged"]!="-1":
            print ("\n** File with merged retrievals' videos are located in: ")
            print(state.state_yt["videos_merged"])
        else:
            print ("An error occurred when merging retrieved video files. \n")


    if len(state.state_yt["comments_files_to_merge"])>0 and (state.ACTION_RETRIEVE_COMMENTS not in state.state_yt["actions"]):
        print ("\n** Sucessive comments retrievals are located in: ")
        for f in state.state_yt["subcomments_files_to_merge"]:
            print (f)

        for f in state.state_yt["comments_files_to_merge"]:
            print(f)


    if len(state.state_yt["comments_merged"])>0:
        if state.state_yt["comments_merged"]!="-1":
            print ("\n** File with merged retrievals' comments are located in: ")
            print(state.state_yt["comments_merged"])
        else:
            print("An error occurred when merging retrieved comments files.")

    if state.state_yt["network_file"]:
        if len(state.state_yt["network_file"]) > 0:
            print("\n** Network file is located in: ")
            print(state.state_yt["network_file"])

    print("\n")
    if len(state.state_yt["actions"])==0:
        if nothing_to_retrieve:
            print ("** No pending actions to retrieve")
        else:
            if success:
                print ("** Retrieving completed")
            else:
                print ("** An error ocurred while retrieving and/or merging files. Please try the request again.")
    else:
        print ("** The following actions will be completed when quote is available: ")
        if (state.ACTION_RETRIEVE_VIDEOS in state.state_yt["actions"]):
            print ("Retrieve videos ")
        if (state.ACTION_RETRIEVE_COMMENTS in state.state_yt["actions"]):
            print("Retrieve comments ")
        if (state.ACTION_CREATE_NETWORK in state.state_yt["actions"]):
            print("Build Network ")




# -----------------------------------------------------------------------------------------------------------------------
# -----------------------------------------------------------------------------------------------------------------------
def notify_user_channel_on_file(text):

    try:
        #Open file
        name = get_filename("summary","txt")
        fullname = get_fullpath("summaries", name)
        fullname_plain = get_fullpath("summaries", "summary.txt")
        f = open(fullname,'w+')

        f.write("\n*****************************************************************\n")
        f.write("Retrieving status\n")
        now = datetime.now()
        dt_string = now.strftime("%b %d %Y %H:%M:%S")
        f.write(dt_string)
        f.write("\n")
        f.write(state.print_quote_usage())

        f.write(text)
        if len(state.state_yt[state.LIST_CHANNELS_TO_MERGE]) > 0:
            f.write("\n** Sucessive channel's retrievals are located in: \n")
            for fn in state.state_yt[state.LIST_CHANNELS_TO_MERGE]:
                f.write(fn)
                f.write("\n")

        if len(state.state_yt[state.CHANNELS_MERGED]) > 0:
            if state.state_yt[state.CHANNELS_MERGED] != "-1":
                f.write("\n** File with merged channel's retrievals are located in: \n")
                f.write(state.state_yt[state.CHANNELS_MERGED])
                f.write("\n")
            else:
                f.write("An error occurred when merging retrieved channel's files. \n")
        else:
            f.write("** The following actions will be completed when quote is available: \n")
            f.write(text)
    except:
        f.write ("An error occurred while creating this summary. \n")

    f.close()
    shutil.copyfile(fullname, fullname_plain)


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def notify_user_channel(text):

    print ("\n*******************************************************************************************")
    print ("Retrieving status")
    now = datetime.now()
    dt_string = now.strftime("%b %d %Y %H:%M:%S")
    print(dt_string)


    state.print_quote_usage()

    print (text)
    if len(state.state_yt[state.LIST_CHANNELS_TO_MERGE])>0:
        print ("\n** Sucessive channel's retrievals are located in: ")
        for f in state.state_yt[state.LIST_CHANNELS_TO_MERGE]:
            print (f)

    if len(state.state_yt[state.CHANNELS_MERGED])>0:
        if state.state_yt[state.CHANNELS_MERGED]!="-1":
            print ("\n** File with merged channel's retrievals are located in: ")
            print(state.state_yt[state.CHANNELS_MERGED])
        else:
            print ("An error occurred when merging retrieved channel's files. \n")
    else:
        print("** The following actions will be completed when quote is available: ")
        print (text)



#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def resume_retrievals():

    print ("************************************************************************************************")
    now = datetime.now()
    dt_string = now.strftime("%b %d %Y %H:%M:%S")
    print(dt_string)
    print ("Running Retriever ....\n")


    #Load current state
    state.state_yt = state.load_state_from_file()
    print ("Current state: \n")
    state.print_state(state.state_yt)
    print ("************************************************************************************************")
    print ("\n")

    if not state.continue_to_retrieve(state.state_yt):
        print ("Out of quote.")
        return

    #There is nothing to retrieve
    if len(state.state_yt[state.LIST_ACTIONS])==0:
        notify_user(nothing_to_retrieve=True)
        notify_user_on_file(nothing_to_retrieve=True)
        state.state_yt = state.clear_state(state.state_yt)
        return

    #Create youtube data api service
    youtube = build_service_api_key()
    #Actions run in a specific order
    #For example, we cannot retrieve comments and then videos.
    #First retrieve videos,then retrieve comments, and then build a network
    #Channel retrieving actions are never in combination

    if state.continue_to_retrieve(state.state_yt) and state.ACTION_RETRIEVE_CHANNELS_METADATA in state.state_yt[state.LIST_ACTIONS]:
        resume_channels_metadata_retrievals(youtube, state.state_yt)
        #Check if the retrieval finished
        if state.ACTION_RETRIEVE_CHANNELS_METADATA not in state.state_yt[state.LIST_ACTIONS]:
            print ("Call procedure to merge files")
            success = output_channel_retrievals(OUTPUT_CHANNEL_METADATA_FILE_NAME)
        notify_user_channel(CHANNEL_METADATA_TEXT)
        notify_user_on_file(CHANNEL_METADATA_TEXT)
        if state.state_yt[state.ALL_CHANNELS_RETRIEVED]:
            state.clear_state(state.state_yt)  # Quote usage remains and it will not be cleared out.
        return

    if state.continue_to_retrieve(state.state_yt) and state.ACTION_RETRIEVE_CHANNELS_ALL_VIDEOS in state.state_yt[
        state.LIST_ACTIONS]:
        resume_channels_all_videos_retrievals(youtube, state.state_yt)
        # Check if the retrieval finished
        if state.ACTION_RETRIEVE_CHANNELS_ALL_VIDEOS not in state.state_yt[state.LIST_ACTIONS]:
            print("Call procedure to merge files")
            success = output_channel_retrievals(OUTPUT_CHANNEL_ALL_VIDEOS_FILE_NAME)
        notify_user_channel(CHANNEL_ALL_VIDEOS_TEXT)
        notify_user_channel_on_file(CHANNEL_ALL_VIDEOS_TEXT)
        if state.state_yt[state.ALL_CHANNELS_RETRIEVED]:
            state.clear_state(state.state_yt)  # Quote usage remains and it will not be cleared out.
        return

    if state.continue_to_retrieve(state.state_yt) and state.ACTION_RETRIEVE_CHANNELS_ACTIVITY in state.state_yt[
        state.LIST_ACTIONS]:
        resume_channels_activity_retrievals(youtube, state.state_yt)
        # Check if the retrieval finished
        if state.ACTION_RETRIEVE_CHANNELS_ACTIVITY not in state.state_yt[state.LIST_ACTIONS]:
            print("\nCalling procedure to merge files \n")
            success = output_channel_retrievals(OUTPUT_CHANNEL_ACTIVITY_FILE_NAME)
        notify_user_channel(CHANNEL_ACTIVITY_TEXT)
        notify_user_channel_on_file(CHANNEL_ACTIVITY_TEXT)
        if state.state_yt[state.ALL_CHANNELS_RETRIEVED]:
            state.clear_state(state.state_yt)  # Quote usage remains and it will not be cleared out.
        return

    if state.continue_to_retrieve(state.state_yt) and state.ACTION_RETRIEVE_VIDEOS in state.state_yt[state.LIST_ACTIONS]:
        resume_video_retrievals(youtube, state.state_yt)

    if state.continue_to_retrieve(state.state_yt) and state.ACTION_RETRIEVE_COMMENTS in state.state_yt[state.LIST_ACTIONS]:
        resume_comments_retrievals(youtube, state.state_yt)

    if (len(state.state_yt[state.LIST_ACTIONS]) == 0) or (
        (len(state.state_yt[state.LIST_ACTIONS]) == 1) and (state.ACTION_CREATE_NETWORK in state.state_yt[state.LIST_ACTIONS])):
        # Only network action should remain, if everything has been processed.
        success = output_retrievals()
        notify_user(success=success)
        notify_user_on_file(success=success)
        state.clear_state(state.state_yt) #Quote usage remains and it will not be cleared out.
    else:
        notify_user()
        notify_user_on_file()


if __name__ == "__main__":
    reset_quote()
    resume_retrievals()
    #state.state_yt = state.load_state_from_file()
    #print ("=======================================")
    #state.print_state(state.state_yt)

    #state.set_quote_usage(state.state_yt, 1000)
    #state.add_action(state.state_yt, state.ACTION_RETRIEVE_VIDEOS)
    #state.print_state(state.state_yt)
    #reset_quote()
    #state.print_state(state.state_yt)