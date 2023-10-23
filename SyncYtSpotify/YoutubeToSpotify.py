import spotipy
from ytmusicapi import YTMusic

from functions import progressbar, print_console_title


class Yt2Sp:
    def __init__(self, yt: YTMusic, sp: spotipy.Spotify, market: list):
        self.yt = yt
        self.sp = sp
        self.market = market

    def sync(self):
        print_console_title('Syncing YouTube Music Likes to Spotify')

        # Get liked songs from YouTube Music
        print('Retrieving liked songs from YouTube Music...')
        yt_liked_songs = self.yt.get_liked_songs(limit=1000000)

        successfully_added = []
        already_added = []
        not_found = []

        for song in progressbar(yt_liked_songs['tracks'], prefix='Syncing to Spotify: '):
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
        with open('yt_to_sp.log', 'w') as f:
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

        print_console_title('Done syncing YouTube Music Likes to Spotify')
