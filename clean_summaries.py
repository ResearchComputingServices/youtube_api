import os
from datetime import datetime
from sys import platform



summary_folder =  "summaries"
output_folder =  "output"
network_folder = "network"
logs_folder = "logs"

summary_days=  30
output_days =  90
network_days = 90
logs_days = 30


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def remove_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def remove_file_older_than(filepath, days):
    if os.path.isfile(filepath):
        if days > 0:
            if platform == "linux" or platform == "linux2":
                file_created_datetime = os.stat(filepath).st_ctime
            elif platform == "darwin":
                file_created_datetime = os.stat(filepath).st_birthtime
            current_datetime = datetime.timestamp(datetime.now())
            dif = current_datetime - file_created_datetime  # Dif in seconds between two days
            # 86400 = Number of secs in 1 day
            old_days = dif / 86400
            # print(old_days)
            if old_days >= days:
                try:
                    os.remove(filepath)
                    # print ('File removed')
                except OSError as e:
                    print("Error: %s : %s" % (filepath, e.strerror))
        else:
            remove_file(filepath)


#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
def clean_history(folder, days=None):
    try:
        if not os.path.exists(folder):
            return

        if not days:
            days = 0

        for path in os.listdir(folder):
            if not path.startswith('.'):
                # It is directory (folder)
                fullpath = os.path.join(folder, path)
                if os.path.isdir(fullpath):
                    # Remove files older than days
                    for file in os.listdir(fullpath):
                        filepath = os.path.join(fullpath, file)
                        remove_file_older_than(filepath, days)
                    # Remove subfolder -if empty
                    try:
                        # print (fullpath)
                        if not os.listdir(fullpath):
                            os.rmdir(fullpath)
                            # print ('Subfolder Removed')
                    except OSError as e:
                        print("Error: %s : %s" % (fullpath, e.strerror))

                if os.path.isfile(fullpath):
                    remove_file_older_than(fullpath, days)

    except OSError as e:
        print("Error: %s : %s" % (folder, e.strerror))

#-----------------------------------------------------------------------------------------------------------------------
#-----------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    current_datetime = datetime.now()
    dt_string = current_datetime.strftime("%d/%m/%Y %H:%M:%S")
    print("Script started at:", dt_string)
    print ('Removing {0} days old files from {1}'.format(summary_days, summary_folder))
    clean_history(summary_folder, summary_days)
    print('Removing {0} days old files from {1}'.format(logs_days, logs_folder))
    current_datetime = datetime.now()
    dt_string = current_datetime.strftime("%d/%m/%Y %H:%M:%S")
    print("Script ended at:", dt_string)


