import os
from os.path import exists
from subprocess import call
from ytmusicapi import YTMusic
from tkinter import *
from tkinter import filedialog


def main():
    # Install dependencies
    print_console_title('Installing dependencies')
    call(['pip3', 'install', '--user', 'ytmusicapi'])
    call(['pip3', 'install', '--user', 'yt-dlp'])

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
    filepath = filedialog.askdirectory(title='Select where to download songs',
                                       initialdir=os.getcwd()) + '/'
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

    # Iterate through liked songs and download them if they haven't been downloaded before
    for idx, song in enumerate(liked_songs['tracks']):
        filename = f'{filepath}{format_song_title(song["title"])}.mp3'
        if not os.path.exists(filename):
            # Convert artists from list to string
            artists = ''
            for artist in song['artists']:
                artists += artist['name'] + ', '
            artists = artists[:-2]

            print_console_title(f'({idx}/{len(liked_songs)}) Downloading {song["title"]} by {artists}')

            download_name = format_song_title(f'{song["title"]}')
            video_url = f'https://music.youtube.com/watch?v={song["videoId"]}'
            call(['yt-dlp', video_url, '-x', '--audio-format', 'mp3', '--audio-quality', '0', '--embed-metadata',
                  '--embed-thumbnail', '-o',
                  f'{filepath}{download_name}.%(ext)s'])

    print_console_title('Done!')


def format_song_title(title: str):
    return title.replace('/', '')


def print_console_title(title: str):
    print('##########################\n' +
          title.upper() + '\n'
                          '##########################\n')


if __name__ == '__main__':
    main()
