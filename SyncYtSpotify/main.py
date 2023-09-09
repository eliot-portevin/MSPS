import json
import sys
from os.path import exists
from subprocess import call
from ytmusicapi import YTMusic
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

'''
See https://colab.research.google.com/github/rruff82/misc/blob/main/YTM2Spotify_clean.ipynb#scrollTo=ehOBPh0NrZmE
for detailed explanations. The authentification process was copied from there.
'''


def main():
    # Check if ytmusicapi is installed
    if 'ytmusicapi' not in sys.modules:
        print('Please install ytmusicapi with:\n'
              '    pip install --user ytmusicapi')
        return

    # Check if Spotify is installed
    if 'spotipy' not in sys.modules:
        print('Please install spotipy with:\n'
              '    pip install --user spotipy')
        return

    # Create authentification files if inexistent
    if not exists('oauth.json'):
        print_console_title('Please follow the instructions to authenticate your Google account')
        call(['ytmusicapi', 'oauth'])

    # Authenticate to YouTube Music
    print_console_title('Loading authentification files')
    ytmusic = YTMusic('oauth.json')

    print_console_title('Authenticating to Spotify')

    # Authenticate to Spotify
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

    market = ["AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY",
              "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU",
              "ID", "IE", "IS", "IT", "JP", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL",
              "NO", "NZ", "PA", "PE", "PH", "PL", "PT", "PY", "SE", "SG", "SK", "SV", "TH", "TR", "TW",
              "US", "UY", "VN"]

    sp_scope = "user-library-read user-library-modify"
    auth_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp_oauth = SpotifyOAuth(
        username=username,
        scope=sp_scope,
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri="https://localhost:8888/callback",
        open_browser=False
    )

    sp = spotipy.Spotify(auth_manager=sp_oauth)
    print(sp.current_user())

    # Get liked songs from YouTube Music
    yt_liked_songs = ytmusic.get_liked_songs(limit=1000000)

    for idx, song in enumerate(yt_liked_songs['tracks']):
        # Convert artists from list to string
        artist = song['artists'][0]['name']
        title = song['title']

        results = sp.search(q=f'{title} - {artist}', type='track', limit=1, market=market)
        items = results['tracks']['items']

        if len(items) == 0:
            print(f'Not found: {title} by {artist}')
        else:
            song_id = items[0]['id']

            if not sp.current_user_saved_tracks_contains([song_id])[0]:
                sp.current_user_saved_tracks_add([song_id])
                print(f'Added: {title} by {artist}')
            else:
                print(f'Already added: {title} by {artist}')


def print_console_title(title: str):
    print('##########################\n' +
          title.upper() + '\n'
                          '##########################\n')


def get_search_string(item):
    return item['artist'] + " - " + item['song']


if __name__ == '__main__':
    main()
