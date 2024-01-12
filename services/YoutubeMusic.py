import os
import time
from subprocess import call
import ytmusicapi
import json

from Track import Track
from cli_functions import *
from streaming_service import StreamingService


class YoutubeMusic(StreamingService):

    def __init__(self):
        super().__init__()
        self.OAUTH_FILENAME = 'config/oauth_ytmusic.json'
        self.MAX_AUTH_ATTEMPTS = 3
        self.service_name = 'YouTube Music'
        self.fetcher = self.authenticate()

    def authenticate(self):
        auth_attempts = 0

        while auth_attempts < self.MAX_AUTH_ATTEMPTS:
            try:
                # Create authentication files if nonexistent
                if not os.path.exists(self.OAUTH_FILENAME):
                    print_message('Authenticating to YouTube Music.')
                    credentials = ytmusicapi.setup_oauth(open_browser=True)

                    with open(self.OAUTH_FILENAME, 'w+') as f:
                        json.dump(credentials, f)

                with open(self.OAUTH_FILENAME, 'r') as f:
                    loaded_credentials = json.load(f)

                return ytmusicapi.YTMusic(self.OAUTH_FILENAME)

            except (json.JSONDecodeError, FileNotFoundError, OSError) as e:
                self.LOGGER.log(f'Error during Youtube Music authentication: {e}' \
                                f'\nDeleting {self.OAUTH_FILENAME} and trying again.')
                os.remove(self.OAUTH_FILENAME)
                auth_attempts += 1

        raise AuthenticationError('Failed to authenticate after multiple attempts.')

    def get_all_playlist_names(self):
        return [
            playlist['title'] for playlist in self.fetcher.get_library_playlists()
            if playlist['title'] not in self.ignored_playlists
        ]

    def get_liked_tracks(self, limit=1000000):
        liked_tracks = self.fetcher.get_liked_songs(limit)['tracks']

        return [extract_track_info(track) for track in liked_tracks]

    def get_tracks_in_playlist(self, playlist_name: str):
        playlists = self.fetcher.get_library_playlists()
        time.sleep(5)
        playlist_id = [playlist['playlistId'] for playlist in playlists if playlist['title'] == playlist_name][0]
        playlist = self.fetcher.get_playlist(playlist_id, 1000000)

        return [extract_track_info(track) for track in playlist['tracks']]

    def add_track_to_playlist(self, playlist_name: str, track: Track):
        try:
            search_results = self.fetcher.search(f'{track.get_title()} - {track.get_artist()}', filter='songs', limit=1)

            playlists = self.fetcher.get_library_playlists()
            playlist_id = [playlist['playlistId'] for playlist in playlists if playlist['title'] == playlist_name][0]

            if len(search_results) == 0:
                self.LOGGER.log(f'YouTube Music: Could not find {track.get_title()} - {track.get_artist()}')

            else:
                song_id = search_results[0]['videoId']

                self.fetcher.add_playlist_items(playlist_id, [song_id])
                self.LOGGER.log(f'YouTube Music: Added {track.get_title()} - {track.get_artist()} to {playlist_name}')
        except Exception as e:
            self.LOGGER.log(f'YouTube Music: Error adding track to playlist - {e}')

    def like_track(self, track: Track):
        search_results = self.fetcher.search(f'{track.get_title()} - {track.get_artist()}', filter='songs', limit=1)

        if len(search_results) == 0:
            self.LOGGER.log(f'YouTube Music: Could not find {track.get_title()} - {track.get_artist()}')

        else:
            song_id = search_results[0]['videoId']
            self.fetcher.rate_song(song_id, 'LIKE')
            self.LOGGER.log(f'YouTube Music: Liked {track.get_title()} - {track.get_artist()}')

    def download_track(self, track: Track) -> bool:
        filepath = os.path.join(os.getcwd(), 'Downloads',
                                f'{format_track_name(track.get_title(), track.get_artist())}.mp3')

        if not os.path.exists(filepath):
            search_results = self.fetcher.search(f'{track.get_title()} - {track.get_artist()}', filter='songs', limit=1)

            if len(search_results) == 0:
                self.LOGGER.log(f'YouTube Music: Could not find {track.get_title()} - {track.get_artist()}')
                return False
            else:
                track_id = search_results[0]['videoId']
                track_url = f'https://music.youtube.com/watch?v={track_id}'
                call(['yt-dlp', track_url, '-x', '--audio-format', 'mp3', '--audio-quality', '0', '--embed-metadata',
                      '--embed-thumbnail', '-o',
                      filepath])
                self.LOGGER.log(f'YouTube Music: Downloaded {track.get_title()} - {track.get_artist()} to local storage')
                return True

    def get_service_name(self):
        return self.service_name

    def create_playlist(self, playlist_name):
        if playlist_name not in self.get_all_playlist_names():
            self.fetcher.create_playlist(playlist_name, 'Imported from Spotify')
            self.LOGGER.log(f'YouTube Music: Created playlist {playlist_name}')


def extract_track_info(track):
    title = track.get('title', '')
    artists = track.get('artists', [])
    artist = artists[0].get('name') if artists else None
    album_info = track.get('album', {})
    album = album_info.get('name') if album_info else None
    duration = track.get('duration')
    return Track(title, artist, album, duration)
