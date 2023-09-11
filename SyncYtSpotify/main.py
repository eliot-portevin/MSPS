import json
import os
import sys
from os.path import exists
from subprocess import call
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth

'''
See https://colab.research.google.com/github/rruff82/misc/blob/main/YTM2Spotify_clean.ipynb#scrollTo=ehOBPh0NrZmE
for detailed explanations. The authentification process was copied from there.
'''


def main():
    # Authenticate to YouTube Music
    yt = authenticate_ytmusic()

    # Authenticate to Spotify
    sp = authenticate_spotify()

    market = ["AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY",
              "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU",
              "ID", "IE", "IS", "IT", "JP", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL",
              "NO", "NZ", "PA", "PE", "PH", "PL", "PT", "PY", "SE", "SG", "SK", "SV", "TH", "TR", "TW",
              "US", "UY", "VN"]

    sync_yt_to_sp(yt, sp, market)

    sync_sp_to_yt(yt, sp, market)


def print_console_title(title: str):
    print('##########################\n' +
          title.upper() + '\n'
                          '##########################\n')


def get_search_string(item):
    return item['artist'] + " - " + item['song']


def authenticate_spotify() -> spotipy.Spotify:
    print('Authenticating to Spotify...')

    if not exists('spotify_oauth.json'):
        client_id = input('Please enter your Spotify client id: ')
        client_secret = input('Please enter your Spotify client secret: ')
        username = input('Please enter your Spotify username: ')

        with open('spotify_oauth.json', 'w') as f:
            json.dump({'client_id': client_id, 'client_secret': client_secret, 'username': username}, f)

    with open('spotify_oauth.json', 'r') as f:
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


def authenticate_ytmusic() -> YTMusic:
    print('Authenticating to YouTube Music...')

    # Create authentification files if inexistent
    if not exists('oauth.json'):
        print_console_title('Please follow the instructions to authenticate your Google account')
        call(['ytmusicapi', 'oauth'])

    # Authenticate to YouTube Music
    return YTMusic('oauth.json')


def sync_yt_to_sp(yt: YTMusic, sp: spotipy.Spotify, market: list):
    print_console_title('Syncing liked songs from YouTube Music to Spotify')

    # Get liked songs from YouTube Music
    print('Retrieving liked songs from YouTube Music...')
    yt_liked_songs = yt.get_liked_songs(limit=1000000)

    successfully_added = []
    already_added = []
    not_found = []

    for song in progressbar(yt_liked_songs['tracks'], prefix='Syncing to Spotify: '):
        # Convert artists from list to string
        artist = song['artists'][0]['name']
        title = song['title']

        results = sp.search(q=f'{title} - {artist}', type='track', limit=1, market=market)
        items = results['tracks']['items']

        if len(items) == 0:
            not_found.append((title, artist))
        else:
            song_id = items[0]['id']

            if not sp.current_user_saved_tracks_contains([song_id])[0]:
                sp.current_user_saved_tracks_add([song_id])
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

    print('Done! Check yt_to_sp.log for results.')


def sync_sp_to_yt(yt: YTMusic, sp: spotipy.Spotify, market: list):
    print_console_title('Syncing liked songs from Spotify to YouTube Music')

    # Get liked songs from Spotify
    print('Retrieving liked songs from Spotify...')
    sp_liked_songs = get_all_saved_tracks_spotify(sp)

    successfully_added = []
    already_added = []
    not_found = []

    for item in progressbar(sp_liked_songs, prefix='Syncing to YouTube Music: '):
        # Convert artists from list to string
        artist = item['track']['artists'][0]['name']
        title = item['track']['name']

        results = yt.search(f'{title} - {artist}', filter='songs', limit=1)

        if len(results) == 0:
            not_found.append((title, artist))
        else:
            song_id = results[0]['videoId']

            yt.rate_song(song_id, 'LIKE')

    # Output results to sp_to_yt.log
    with open('sp_to_yt.log', 'w') as f:
        f.write('Successfully added:\n')
        for title, artist in successfully_added:
            f.write(f'{title} - {artist}\n')

        print('\n\n\n\n')

        f.write('\nNot found:\n')
        for title, artist in not_found:
            f.write(f'{title} - {artist}\n')


def progressbar(it, prefix="Calculating", out=sys.stdout):
    count = len(it)

    # Calculate size of progress bar
    try:
        size = abs(os.get_terminal_size().columns - len(prefix) - 20)
    except OSError:
        size = 50

    def show(j):
        x = int(size * j / count)
        print(f"{prefix}[{u'█' * x}{('.' * (size - x))}] {j}/{count}", end='\r', file=out, flush=True)

    show(0)
    for i, item in enumerate(it):
        yield item
        show(i + 1)
    print("\n", flush=True, file=out)


def get_all_saved_tracks_spotify(sp, limit_step=50):
    offset = 0
    tracks = []
    response = sp.current_user_saved_tracks(limit=limit_step, offset=offset)

    while response['items']:
        tracks.extend(response['items'])
        offset += limit_step
        response = sp.current_user_saved_tracks(limit=limit_step, offset=offset)

    return tracks

if __name__ == '__main__':
    main()