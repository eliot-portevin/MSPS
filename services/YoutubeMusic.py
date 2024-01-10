from os.path import exists
from subprocess import call
from tkinter import Tk, filedialog

from ytmusicapi import YTMusic

from logger import Logger
from streaming_service import StreamingService
from cli_functions import *
from Track import Track


class YoutubeMusic(StreamingService):

    def __init__(self):
        super().__init__()
        self.oauth_filename = 'oauth.json'
        self.fetcher = self.authenticate()

    def authenticate(self):
        # Create authentification files if inexistent
        if not exists(self.oauth_filename):
            print_console_title('Please follow the instructions to authenticate your Google account')
            call(['ytmusicapi', 'oauth'])

        # Authenticate to YouTube Music
        return YTMusic(self.oauth_filename)

    def get_all_playlist_names(self):
        pass

    def get_liked_tracks(self, limit=1000000):
        liked_tracks = self.fetcher.get_liked_songs(limit)['tracks']

        return [extract_track_info(track) for track in liked_tracks]

    def get_tracks_in_playlist(self, playlist_name: str):
        pass

    def add_track_to_playlist(self, playlist_name: str, songs: list):
        pass

    def like_track(self, track: Track):
        search_results = self.fetcher.search(f'{track.get_title()} - {track.get_artist()}', filter='songs', limit=1)

        if len(search_results) == 1:
            self.LOGGER.log(f'YouTube Music: Could not find {track.get_title()} - {track.get_artist()}')

        else:
            song_id = search_results[0]['videoId']
            self.fetcher.rate_song(song_id, 'LIKE')
            self.LOGGER.log(f'YouTube Music: Liked {track.get_title()} - {track.get_artist()}')

    def download_track(self, track: Track):
        # Ask where to download songs
        root = Tk()
        root.withdraw()

        filepath = os.path.join(os.getcwd(), 'Downloads',
                                f'{format_track_name(track.get_title(), track.get_artist())}.mp3')

        if not os.path.exists(filepath):
            search_results = self.fetcher.search(f'{track.get_title()} - {track.get_artist()}', filter='songs', limit=1)
            track_id = search_results[0]['videoId']
            track_url = f'https://music.youtube.com/watch?v={track_id}'
            call(['yt-dlp', track_url, '-x', '--audio-format', 'mp3', '--audio-quality', '0', '--embed-metadata',
                  '--embed-thumbnail', '-o',
                  filepath])
            self.LOGGER.log(f'YouTube Music: Downloaded {track.get_title()} - {track.get_artist()} to local storage')


def extract_track_info(track):
    title = track.get('title')

    artists = track.get('artists', [])
    artist = artists[0]['name'] if artists and artists[0].get('name') else None

    album_info = track.get('album', {})
    album = album_info.get('name') if album_info and album_info.get('name') else None

    duration = track.get('duration')

    return Track(title, artist, album, duration)
