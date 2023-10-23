import spotipy
from ytmusicapi import YTMusic

from functions import progressbar, print_console_title


class Yt2Sp:
    def __init__(self, yt: YTMusic, sp: spotipy.Spotify, market: list):
        self.yt = yt
        self.sp = sp
        self.market = market

        self.spotify_playlists = self.sp.user_playlists(self.sp.current_user()['id'])
        print(self.spotify_playlists)

    def sync(self, sync_likes=True, sync_user_playlists=False):
        playlists = self.get_playlist_list()

        for playlist_info in playlists:
            if playlist_info['title'] == 'Liked Music' and sync_likes:
                self.sync_playlist(playlist_info)
            elif sync_user_playlists:
                self.sync_playlist(playlist_info)

    def sync_playlist(self, playlist_info):
        print(f'Retrieving playlist {playlist_info["title"]} from YouTube Music...')
        playlist = self.get_playlist(playlist_info['playlistId'])

        # Check if playlist already exists on Spotify
        sp_list_id = ''


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

                if not self.sp.current_user_saved_tracks_contains([song_id])[0]:
                    self.sp.current_user_saved_tracks_add([song_id])
                    successfully_added.append((title, artist))
                else:
                    already_added.append((title, artist))

        # Output results to yt_to_sp.log
        with open('yt_to_sp.log', 'a') as f:
            f.write(f'\n\n####################\n{playlist["title"]}\n####################\n\n')
            f.write('Successfully added:\n')
            for title, artist in successfully_added:
                f.write(f'{title} - {artist}\n')

            print('\n\n\n\n')

            f.write('\nAlready added:\n')
            for title, artist in already_added:
                f.write(f'{title} - {artist}\n')

            print('\n\n\n\n')

            f.write('\nNot found:\n')
            for title, artist in not_found:
                f.write(f'{title} - {artist}\n')

    def get_playlist_list(self):
        print_console_title('Retrieving playlists from YouTube Music')
        playlists = self.yt.get_library_playlists(limit=1000)
        return playlists

    def get_playlist(self, playlist_id):
        playlist = self.yt.get_playlist(playlist_id)
        return playlist
