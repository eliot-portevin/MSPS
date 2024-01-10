from os.path import exists
from subprocess import call
from ytmusicapi import YTMusic

from Logger import Logger
from StreamingService import StreamingService
from CLI import *
from Track import Track


class YoutubeMusic(StreamingService):

    def __init__(self):
        super().__init__()
        self.oauth_filename = '../oauth.json'
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


def extract_track_info(track):
    title = track.get('title')

    artists = track.get('artists', [])
    artist = artists[0]['name'] if artists and artists[0].get('name') else None

    album_info = track.get('album', {})
    album = album_info.get('name') if album_info and album_info.get('name') else None

    duration = track.get('duration')

    return Track(title, artist, album, duration)
