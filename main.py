from argparse import ArgumentParser
from services.Spotify import Spotify
from services.YoutubeMusic import YoutubeMusic
import time
from sys import exit

from cli_functions import *
from streaming_service import StreamingService
from menu import Menu


'''
See https://colab.research.google.com/github/rruff82/misc/blob/main/YTM2Spotify_clean.ipynb#scrollTo=ehOBPh0NrZmE
for detailed explanations. The authentification process was copied from there.
'''


def main():
    services = {'Youtube Music': YoutubeMusic,
                'Spotify': Spotify}

    run_menu_source(services)


# Menu responsible for determining which platform tracks will be imported from
def run_menu_source(services):
    title = "Hi! Welcome to the Music Streaming Platform Synchroniser." \
            "\nPress Q or Esc to Quit." \
            "\nPlease select the platform which you'd like to import from:" \
            "\n"
    items = list(services.keys())

    menu = Menu(title = title,
                items = items,
                exitOption = True)

    running = True

    while running:
        selection = menu.get_selection()

        if menu.has_requested_return(selection):
            running = False

        else:
            source = services.get(selection)()

            run_menu_destination(
                {key:services[key] for key in services if key != selection},
                source)


def run_menu_destination(services, source: StreamingService):
    download_locally_string = 'Download locally'
    title = 'Which platform would you like to export to?'
    items = list(services.keys()) + [download_locally_string]

    menu = Menu(title = title,
                items = items)

    running = True

    while running:
        selection = menu.get_selection()

        if menu.has_requested_return(selection):
            running = False

        elif selection == download_locally_string:
            download_tracks(source)
            running = False

        else:
            destination = services.get(selection)()

            transfer_likes(source, destination)
            running = False


def download_tracks(source: StreamingService):
    title = 'MSPS uses yt-dlp to download your tracks from the Youtube Music database.' \
            f'\nIt is about to import your liked songs from {source.get_service_name()}.' \
            f'\nHow many would you like to be downloaded (approximate number, the api tends to just do its thing)?'
    items = {'10': 10,
            '50': 50,
            '100': 100,
            '200': 200,
            '1000': 1000,
            'all': 1000000}

    menu = Menu(title, items)
    selection = menu.get_selection()

    if menu.has_requested_return(selection):
        return

    else:
        limit = items.get(selection)

    print(f'Download of {limit} tracks has been requested')
    time.sleep(5)


def transfer_likes(source: StreamingService, destination: StreamingService):
    # liked_tracks = source.get_liked_tracks()

    # for track in progressbar(liked_tracks, 'Liking Tracks'):
    #     destination.like_track(track)

    print(f'Syncing likes from {source.get_service_name} to {destination.get_service_name}')
    time.sleep(3)


if __name__ == '__main__':
    main()
