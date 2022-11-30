from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import pickle
from utils import *



#*****************************************************************************************************
#Builds a service for the YouTube Data API using oauth credentials
#With oauth credentials other request in addition to retrieving information (like updates or inserts)
#in a user autorized youtube channels can be executed
#*****************************************************************************************************
def build_service_oauth():

    credentials = None
    # token.pickle stores the user's credentials from previously successful logins
    if os.path.exists('token.pickle'):
        print('Loading Credentials From File...')
        with open('token.pickle', 'rb') as token:
            credentials = pickle.load(token)

    # If there are no valid credentials available, then either refresh the token or log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print('Refreshing Access Token...')
            try:
                credentials.refresh(Request())
            except:
                if os.path.exists('token.pickle'):
                    os.remove('token.pickle')
                    print ("Please run the app again.")
                else:
                    print ("Unexpected error when attempting to login")
                return

        else:
            print('Fetching New Tokens...')
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=[
                    'https://www.googleapis.com/auth/youtube.readonly',
                    'https://www.googleapis.com/auth/youtube.force-ssl'
                ]
            )

            flow.run_local_server(port=8080, prompt='consent',
                                  authorization_prompt_message='')
            credentials = flow.credentials

            # Save the credentials for the next run
            with open('token.pickle', 'wb') as f:
                print('Saving Credentials for Future Use...')
                pickle.dump(credentials, f)

    # Builds a service object. In this case, the service is youtube api, version v3, with OAuth credentials
    youtube = build('youtube', 'v3', credentials=credentials)
    return youtube


#*****************************************************************************************************
#Builds a service for the YouTube Data API using an API Key
#This is the simplest form of authentication and it is available only to retrieve public information
#*****************************************************************************************************
def build_service_api_key():
    api_key = get_api_key()
    youtube = None

    if api_key:
        # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
        youtube = build('youtube', 'v3', developerKey=api_key)

    return youtube
