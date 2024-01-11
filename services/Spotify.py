import json
import time
from os.path import exists

import spotipy
from spotipy import SpotifyOAuth

from cli_functions import *
from streaming_service import StreamingService
from Track import Track


class Spotify(StreamingService):

    def __init__(self):
        super().__init__()
        self.oauth_filename = 'oauth_spotify.json'
        self.service_name = 'Spotify'
        self.fetcher = self.authenticate()

    def authenticate(self):
        if not exists('oauth_spotify.json'):
            print_console_title('Please follow the instructions to authenticate your Spotify account')
            client_id = input('Please enter your Spotify client id: ')
            client_secret = input('Please enter your Spotify client secret: ')
            username = input('Please enter your Spotify username: ')

            with open('oauth_spotify.json', 'w') as f:
                json.dump({'client_id': client_id, 'client_secret': client_secret, 'username': username}, f)
                print('Saved authentication data to oauth_spotify.json')

        with open(self.oauth_filename, 'r') as f:
            data = json.load(f)

        client_id = data['client_id']
        client_secret = data['client_secret']
        username = data['username']

        sp_scope = ("user-library-read"
                    " user-library-modify"
                    " playlist-read-private"
                    " playlist-modify-public"
                    " playlist-modify-private")
        sp_oauth = SpotifyOAuth(
            username=username,
            scope=sp_scope,
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="https://localhost:8888/callback",
            open_browser=False
        )

        return spotipy.Spotify(auth_manager=sp_oauth)

    def get_all_playlist_names(self):
        playlists = self.get_user_playlists()

        return [playlist['name'] for playlist in playlists if playlist['name'] not in self.ignored_playlists]

    def get_liked_tracks(self, limit=1000000):
        offset = 0
        tracks = []
        limit_step = 50

        response = self.fetcher.current_user_saved_tracks(limit=limit_step, offset=offset)

        while response['items'] and len(tracks) < limit:
            tracks.extend(response['items'])
            offset += limit_step
            response = self.fetcher.current_user_saved_tracks(limit=limit_step, offset=offset)

        return [extract_track_info(track) for track in tracks]

    def get_tracks_in_playlist(self, playlist_name: str):
        playlist_id = [playlist['id'] for playlist in self.get_user_playlists() if playlist['name'] == playlist_name][0]

        offset = 0
        tracks = []
        limit_step = 100

        response = self.fetcher.playlist_items(playlist_id, limit=limit_step, offset=offset)

        while response['items']:
            tracks.extend(response['items'])
            offset += limit_step
            response = self.fetcher.playlist_items(playlist_id, limit=limit_step, offset=offset)

        return [extract_track_info(track) for track in tracks]

    # Adds a track to an playlist. This function assumes that the playlist exists and that the track is not already in
    # it. Refer to create_playlist() and get_tracks_in_playlist() for more information.
    def add_track_to_playlist(self, playlist_name: str, track: Track):
        try:
            search_results = self.fetcher.search(f'{track.get_title()} - {track.get_artist()}', type='track', limit=1)

            if len(search_results['tracks']['items']) == 0:
                self.LOGGER.log(f'Spotify: Could not find {track.get_title()} - {track.get_artist()}')

            else:
                song_id = search_results['tracks']['items'][0]['id']
                playlist_id = [playlist['id'] for playlist in self.get_user_playlists()
                               if playlist['name'] == playlist_name][0]
                self.fetcher.playlist_add_items(playlist_id, [song_id])
                self.LOGGER.log(f'Spotify: Added {track.get_title()} - {track.get_artist()} to {playlist_name}')

        except Exception as e:
            self.LOGGER.log(f'Spotify: Error adding track to playlist - {e}')

    def like_track(self, track: Track):
        search_results = self.fetcher.search(f'{track.get_title()} - {track.get_artist()}', type='track', limit=1)

        if len(search_results['tracks']['items']) == 0:
            self.LOGGER.log(f'Spotify: Could not find {track.get_title()} - {track.get_artist()}')

        else:
            song_id = search_results['tracks']['items'][0]['id']
            self.fetcher.current_user_saved_tracks_add([song_id])
            self.LOGGER.log(f'Spotify: Liked {track.get_title()} - {track.get_artist()}')

    def get_service_name(self):
        return self.service_name

    def get_user_playlists(self):
        playlists = []

        offset = 0
        limit_step = 50
        response = self.fetcher.current_user_playlists(limit=limit_step, offset=offset)

        while response['items']:
            playlists.extend(response['items'])
            offset += limit_step
            response = self.fetcher.current_user_playlists(limit=limit_step, offset=offset)

        return playlists

    def create_playlist(self, playlist_name: str):
        if playlist_name not in self.get_all_playlist_names():
            self.fetcher.user_playlist_create(self.fetcher.me()['id'], playlist_name)
            self.LOGGER.log(f'Spotify: Created playlist {playlist_name}')


def extract_track_info(track):
    title = track['track']['name']
    artist = track['track']['artists'][0]['name']
    album = track['track']['album']['name']
    duration = track['track']['duration_ms']

    return Track(title, artist, album, duration)
