import sys
from subprocess import call
from ytmusicapi import YTMusic
from tkinter import *
from tkinter import filedialog
import os
from os.path import exists

"""
Install ytmusicapi with:
    pip3 install --user ytmusicapi
    
Install yt-dlp with:
    pip3 install --user yt-dlp
"""


def main():
    # Check if ytmusicapi is installed
    if 'ytmusicapi' not in sys.modules:
        print('Please install ytmusicapi with:\n'
              '    pip3 install --user ytmusicapi')
        return

    # Check if yt-dlp is installed
    if 'yt_dlp' not in sys.modules:
        print('Please install yt-dlp with:\n'
              '    pip3 install --user yt-dlp')
        return

    # Create authentification file if it doesn't exist
    if not exists('oauth.json'):
        print_console_title('Please follow the instructions to authenticate your Google account')
        call(['ytmusicapi', 'oauth'])

    # Load authentification file
    print_console_title('Loading authentification file')
    ytmusic = YTMusic('oauth.json')

    # Ask where to download songs
    root = Tk()
    root.withdraw()
    directory = filedialog.askdirectory(title='Select where to download songs',
                                        initialdir=os.getcwd())

    root.destroy()

    # Request number of liked songs to download
    n = -1
    while n < 0:
        try:
            n = int(input('How many songs do you want to download?\n'
                          '>> '))
        except ValueError:
            print('Please enter a valid number.')

    # Get liked songs. Returns a dictionary of the n last liked musics containing their video id, privacy, title,
    # thumbnails, description, trackCount, views, tracks and duration (in seconds). Songs are stored in the tracks key
    print_console_title('Retrieving liked songs from YouTube Music')
    liked_songs = ytmusic.get_liked_songs(limit=n)

    # Find songs that have already been downloaded
    to_download = []
    for idx, song in enumerate(liked_songs['tracks']):
        filepath = os.path.join(directory, f'{format_song_title(song["title"])}.mp3')

        if not os.path.exists(filepath):
            to_download.append((song, filepath))

    # Download songs
    for idx, tuple in enumerate(to_download):
        song = tuple[0]
        filepath = tuple[1]

        # Convert artists from list to string
        artists = ''
        for artist in song['artists']:
            artists += artist['name'] + ', '
        artists = artists[:-2]

        print_console_title(f'({idx}/{len(to_download)}) Downloading {song["title"]} by {artists}')

        video_url = f'https://music.youtube.com/watch?v={song["videoId"]}'
        call(['yt-dlp', video_url, '-x', '--audio-format', 'mp3', '--audio-quality', '0', '--embed-metadata',
              '--embed-thumbnail', '-o',
              filepath])

    print('Done!')


def format_song_title(title: str):
    return title.replace('/', '')


def print_console_title(title: str):
    print('##########################\n' +
          title.upper() + '\n'
                          '##########################\n')


if __name__ == '__main__':
    main()
