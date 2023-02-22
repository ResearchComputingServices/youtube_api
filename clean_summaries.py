import os
from datetime import datetime


summary_folder =  "summary"
output_folder =  "output"
network_folder = "network"
logs_folder = "logs"

summary_days=  30
output_days =  90
network_days = 90
logs_days = 30


def clean_history(self, folder, remove_folder, days=None):
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
                        self.remove_file_older_than(filepath, days)
                    # Remove subfolder -if empty
                    try:
                        # print (fullpath)
                        if not os.listdir(fullpath):
                            os.rmdir(fullpath)
                            # print ('Subfolder Removed')
                    except OSError as e:
                        print("Error: %s : %s" % (fullpath, e.strerror))

                if os.path.isfile(fullpath):
                    self.remove_file_older_than(fullpath, days)

        if remove_folder:
            self.remove_folder(folder)
    except OSError as e:
        print("Error: %s : %s" % (folder, e.strerror))


if __name__ == '__main__':
    current_datetime = datetime.now()
    dt_string = current_datetime.strftime("%d/%m/%Y %H:%M:%S")
    print("Script started at:", dt_string)
    print ('Removing {0} days old files from {1}'.format(summary_days, summary_folder))
    clean_history(summary_folder, False, summary_days)
    print('Removing {0} days old files from {1}'.format(logs_days, logs_folder))
    current_datetime = datetime.now()
    dt_string = current_datetime.strftime("%d/%m/%Y %H:%M:%S")
    print("Script ended at:", dt_string)


