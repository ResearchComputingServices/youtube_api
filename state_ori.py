import pickle
import pathlib
import os
from werkzeug.utils import secure_filename


STATE_DIRECTORY = "state"
STATE_FILENAME = "state.pkl"

def get_quote_filename():
    directory = STATE_DIRECTORY
    name = STATE_FILENAME
    abs_path = pathlib.Path().resolve()
    full_path = os.path.join(abs_path, directory)
    filename = secure_filename(name)
    filename_path = os.path.join(full_path, filename)
    return filename_path

class State:
    api_key = ""
    quote_usage = 0
    actions = []
    videos_ids_file = ""
    videos_files_to_merge =[]
    comments_files_to_merge = []
    network_files_to_merge = []
    index = 0
    pending = False

  #  def __init__(self, api_key, quote_usage, actions, videos_ids_file):
  #      self.api_key = api_key
  #      self.quote_usage = quote_usage
  #      self.videos_ids_file = videos_ids_file

    def save_state_to_file(self):
        filename_path = get_quote_filename()
        state = State()
        with open(filename_path, 'wb') as file:
            pickle.dump(state, file)

    def set_quote_usage(self, value):
        self.quote_usage = value
        save_state_to_file(self)


    def set_api_key(self, value):
        self.api_key = value
        save_state_to_file(self)

    def add_action(self, action):
        if action and action not in self.actions:
            self.actions.append(action)
            save_state_to_file(self)

    def remove_action(self, action=None, all=None):

        if action and action in self.actions:
            self.actions.remove(action)

        if all:
            self.actions = []

        self.save_state_to_file()

    def print_state(self):
        print(self.api_key)
        print(self.quote_usage)
        print(self.actions)

state_yt = State()


def load_state_from_file():
    obj = None
    file = get_quote_filename()
    if os.path.exists(file):
        with open(file, 'rb') as f:
            obj = pickle.load(f)
            print (obj.api_key)
            print (obj.quote_usage)
            print (obj.actions)
    return obj





