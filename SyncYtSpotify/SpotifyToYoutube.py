import spotipy
from ytmusicapi import YTMusic

from functions import progressbar, print_console_title


class Sp2Yt:
    def __init__(self, yt: YTMusic, sp: spotipy.Spotify):
        self.yt = yt
        self.sp = sp

    def sync(self):
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

        # Output results to sp_to_yt.log
        with open('sp_to_yt.log', 'w') as f:
            f.write('Successfully added:\n')
            for title, artist in successfully_added:
                f.write(f'{title} - {artist}\n')

            print('\n\n\n\n')

            f.write('\nNot found:\n')
            for title, artist in not_found:
                f.write(f'{title} - {artist}\n')

        print_console_title('Done syncing Spotify Likes to YouTube Music')

    def get_all_saved_tracks(self, limit_step=50):
        offset = 0
        tracks = []
        response = self.sp.current_user_saved_tracks(limit=limit_step, offset=offset)

        while response['items']:
            tracks.extend(response['items'])
            offset += limit_step
            response = self.sp.current_user_saved_tracks(limit=limit_step, offset=offset)

        return tracks
