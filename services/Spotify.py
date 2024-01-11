import json
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

        sp_scope = "user-library-read user-library-modify"
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
        pass

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
        pass

    def add_track_to_playlist(self, playlist_name: str, songs: list):
        pass

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

def extract_track_info(track):
    title = track['track']['name']
    artist = track['track']['artists'][0]['name']
    album = track['track']['album']['name']
    duration = track['track']['duration_ms']

    return Track(title, artist, album, duration)
