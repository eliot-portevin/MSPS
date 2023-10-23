import spotipy
from ytmusicapi import YTMusic
from pythonlangutil.overload import Overload, signature

from functions import progressbar, print_console_title


class Yt2Sp:
    def __init__(self, yt: YTMusic, sp: spotipy.Spotify, market: list):
        self.yt = yt
        self.sp = sp
        self.market = market

        self.spotify_playlists = self.sp.user_playlists(self.sp.current_user()['id'])
        self.ignored_playlists = ['Episodes for Later', 'Liked Music']

    def sync(self, sync_likes=True, sync_user_playlists=False):
        if sync_likes:
            self.sync_likes()

        if sync_user_playlists:
            playlists = self.get_playlist_list()

            for playlist in playlists:
                if playlist['title'] in self.ignored_playlists:
                    playlists.remove(playlist)

            print('Found playlists:')
            for playlist in playlists:
                print('- ' + playlist['title'])

            for playlist_info in playlists:
                self.sync_playlist(playlist_info)

    def sync_likes(self):
        print('Syncing Spotify Likes to YouTube Music')

        # Get liked songs from Spotify
        print('Retrieving liked songs from Spotify...')
        sp_liked_songs = self.get_all_saved_tracks()

        successfully_added = []
        not_found = []

        for item in progressbar(sp_liked_songs, prefix='Syncing to YouTube Music: '):
            # Convert artists from list to string
            artist = item['track']['artists'][0]['name']
            title = item['track']['name']

            results = self.yt.search(f'{title} - {artist}', filter='songs', limit=1)

            if len(results) == 0:
                not_found.append((title, artist))
            else:
                song_id = results[0]['videoId']
                self.yt.rate_song(song_id, 'LIKE')

    def sync_playlist(self, playlist_info):
        print(f'Retrieving playlist {playlist_info["title"]} from YouTube Music...')
        playlist = self.get_playlist(playlist_info['playlistId'])

        # Check if playlist already exists on Spotify, if not create it
        if playlist_info['title'] in [item['name'] for item in self.spotify_playlists['items']]:
            for item in self.spotify_playlists['items']:
                if item['name'] == playlist_info['title']:
                    sp_list_id = item['id']
                    break

        else:
            sp_list_id = self.sp.user_playlist_create(self.sp.current_user()['id'],
                                                      playlist_info['title'])['id']

        # Get songs from Spotify playlist (to check if songs are already in playlist)
        spotify_playlist_songs = self.get_tracks_playlist(sp_list_id)

        # Set playlist privacy
        public = self.yt.get_playlist(playlist_info['playlistId'])['privacy'] == 'PUBLIC'
        self.sp.playlist_change_details(sp_list_id, public=public)

        successfully_added = []
        already_added = []
        not_found = []

        for song in progressbar(playlist['tracks'], prefix=f'Syncing playlist {playlist_info["title"]} to Spotify: '):
            # Convert artists from list to string
            artist = song['artists'][0]['name']
            title = song['title']

            results = self.sp.search(q=f'{title} - {artist}', type='track', limit=1, market=self.market)
            items = results['tracks']['items']

            if len(items) == 0:
                not_found.append((title, artist))
            else:
                song_id = items[0]['id']

                if not any(song_id == item['track']['id'] for item in spotify_playlist_songs):
                    self.add_song_to_playlist(sp_list_id, song_id)
                    successfully_added.append((title, artist))
                else:
                    already_added.append((title, artist))

    def get_playlist_list(self):
        print_console_title('Retrieving playlists from YouTube Music')
        playlists = self.yt.get_library_playlists(limit=1000)
        return playlists

    def get_playlist(self, playlist_id):
        playlist = self.yt.get_playlist(playlist_id)
        return playlist

    @Overload
    @signature('str')
    def add_song_to_playlist(self, song_id):
        self.sp.current_user_saved_tracks_add([song_id])

    @add_song_to_playlist.overload
    @signature('str', 'str')
    def add_song_to_playlist(self, playlist_id, song_id):
        # Overload for adding song to playlist instead of liked songs
        self.sp.playlist_add_items(playlist_id, [song_id])

    def get_tracks_playlist(self, playlist_id, limit_step=50):
        offset = 0
        tracks = []
        response = self.sp.playlist_items(playlist_id, limit=limit_step, offset=offset)

        while response['items']:
            tracks.extend(response['items'])
            offset += limit_step
            response = self.sp.playlist_items(playlist_id, limit=limit_step, offset=offset)

        return tracks
