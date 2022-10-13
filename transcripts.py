import os
import pathlib
import traceback
import sys
from youtube_transcript_api import YouTubeTranscriptApi
from werkzeug.utils import secure_filename



def write_transcript_to_file(transcript,video_title,video_id):
    try:

        directory = 'transcripts'
        abs_path = pathlib.Path().resolve()
        full_path = os.path.join(abs_path, directory)
        name = video_title + '_' + video_id + '.txt'
        filename = secure_filename(name)
        file_path = os.path.join(full_path, filename)

        with open(file_path, 'w') as f:
            for item in transcript:
                start = item.get('start',0.0)
                duration = item.get('duration',0.0)
                text = item.get('text')
                line = "{},{}\n{}\n".format(str(start),str(start+duration),text)
                f.write('%s\n' % (line))
    except:
        print("Error on writing transcript file for video: " + video_title)
        print(sys.exc_info()[0])
        traceback.print_exc()
        if os.path.exists(file_path):
            os.remove(file_path)
        file_path = ''

    return file_path




def get_video_transcript(videoId):

    transcript_data={}
    try:
        # Get transcripts
        transcript_list = YouTubeTranscriptApi.list_transcripts(videoId)
        if transcript_list:
            # Priority to manual added transcript
            for transcript in transcript_list:
                if not transcript.is_generated:
                    if 'en' in transcript.language_code.lower():
                        transcript_data["tr_type"] = "Manual"
                        transcript_data["language"] = transcript.language_code
                        transcript_data["data"] = transcript.fetch()
                        return transcript_data

            # Then automatically generated
            for transcript in transcript_list:
                if 'en' in transcript.language_code.lower():
                    transcript_data["tr_type"] = "Generated"
                    transcript_data["language"] = transcript.language_code
                    transcript_data["data"] = transcript.fetch()
                    return transcript_data

            # Translated
            for transcript in transcript_list:
                # translating the transcript will return another transcript object
                transcript_data["tr_type"] = "Translated from " + transcript.language_code
                transcript_data["language"] = "English"
                transcript_data["data"] = transcript.translate('en').fetch()
                return transcript_data
    except:
        print ('No transcript available.')

    transcript_data["tr_type"] = ""
    transcript_data["language"] = ""
    transcript_data["data"] = ""

    return transcript_data

