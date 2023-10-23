import json
from argparse import ArgumentParser
from os.path import exists
from subprocess import call

import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic

from YoutubeToSpotify import Yt2Sp
from SpotifyToYoutube import Sp2Yt
from functions import *

'''
See https://colab.research.google.com/github/rruff82/misc/blob/main/YTM2Spotify_clean.ipynb#scrollTo=ehOBPh0NrZmE
for detailed explanations. The authentification process was copied from there.
'''


def main():
    parser = ArgumentParser(description='Synchronise your liked songs between YouTube Music and Spotify.')
    parser.add_argument('--yt2sp', action='store_true', help='Sync liked songs from YouTube Music to Spotify')
    parser.add_argument('--sp2yt', action='store_true', help='Sync liked songs from Spotify to YouTube Music')
    parser.add_argument('--all', action='store_true', help='Sync liked songs from YouTube Music to Spotify and vice '
                                                           'versa')

    args = parser.parse_args()

    if any(vars(args).values()):
        # Authenticate to YouTube Music
        yt = authenticate_yt_music()

        # Authenticate to Spotify
        sp = authenticate_spotify()

        market = ["AD", "AR", "AT", "AU", "BE", "BG", "BO", "BR", "CA", "CH", "CL", "CO", "CR", "CY",
                  "CZ", "DE", "DK", "DO", "EC", "EE", "ES", "FI", "FR", "GB", "GR", "GT", "HK", "HN", "HU",
                  "ID", "IE", "IS", "IT", "JP", "LI", "LT", "LU", "LV", "MC", "MT", "MX", "MY", "NI", "NL",
                  "NO", "NZ", "PA", "PE", "PH", "PL", "PT", "PY", "SE", "SG", "SK", "SV", "TH", "TR", "TW",
                  "US", "UY", "VN"]

        if args.yt2sp:
            yt2sp = Yt2Sp(yt, sp, market)
            yt2sp.sync()
        elif args.sp2yt:
            sp2yt = Sp2Yt(yt, sp)
            sp2yt.sync()
        elif args.all:
            yt2sp = Yt2Sp(yt, sp, market)
            yt2sp.sync()
            sp2yt = Sp2Yt(yt, sp)
            sp2yt.sync()
    else:
        parser.print_help()


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


def authenticate_yt_music() -> YTMusic:
    print('Authenticating to YouTube Music...')

    # Create authentification files if inexistent
    if not exists('oauth.json'):
        print_console_title('Please follow the instructions to authenticate your Google account')
        call(['ytmusicapi', 'oauth'])

    # Authenticate to YouTube Music
    return YTMusic('oauth.json')


if __name__ == '__main__':
    main()
