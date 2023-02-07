import argparse
import sys
import os.path


def get_input_arguments():
    my_parser = argparse.ArgumentParser(description='YouTube API scrapper')

    my_parser.add_argument('-o',
                           '--option',
                            action='store',
                            help='YouTube API Menu Option (3, 4, 5, 6, or 7)')

    my_parser.add_argument('-p',
                            '--playlist',
                            action='store',
                            help='Playlist to retrieve (for options: 3, 4, or 5)')

    my_parser.add_argument('-q',
                           '--query',
                           action='store',
                           help='Query to search (for options: 6 or 7)')

    my_parser.add_argument('-v',
                           '--videos',
                           action='store',
                           help='Number of videos to search (for options: 6 or 7)')

    # Execute the parse_args() method
    args = my_parser.parse_args()

    option = args.option
    playlist = args.playlist
    query = args.query

    return option, playlist, query
