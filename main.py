from argparse import ArgumentParser

from simple_term_menu import TerminalMenu
from services.Spotify import Spotify
from services.YoutubeMusic import YoutubeMusic
from cli_functions import *
from streaming_service import StreamingService

import time


'''
See https://colab.research.google.com/github/rruff82/misc/blob/main/YTM2Spotify_clean.ipynb#scrollTo=ehOBPh0NrZmE
for detailed explanations. The authentification process was copied from there.
'''


def main():
    # parser = ArgumentParser(description='Synchronise your music streaming services.')
    # parser.add_argument('--source', choices=['yt', 'sp'], help='Source streaming service')
    # parser.add_argument('--destination', choices=['yt', 'sp'], help='Destination streaming service')
    # parser.add_argument('--action', choices=['like', 'download'], help='Action to perform')
    # args = parser.parse_args()

    services = {'Youtube Music': YoutubeMusic,
                'Spotify': Spotify}

    menu_main_title = "Hi! Welcome to the Music Streaming Platform Synchroniser." \
                      "\nPress Q or Esc to Quit." \
                      "\nPlease select the platform which you'd like to import from:" \
                      "\n"
    menu_main_items = list(services.keys()) + ['Quit']

    menu_destination_title = 'Which platform would you like to export to?'
    menu_destination_items = list(services.keys()) + ['Download locally', 'Back']

    main_menu = create_menu(menu_main_title, menu_main_items)
    destination_menu = create_menu(menu_destination_title, menu_destination_items)

    running_main_menu = True
    local_download = False

    while running_main_menu:
        main_selection = main_menu.show()

        # Quit
        if main_selection == len(main_menu._menu_entries)-1 or main_selection == None:
            running_main_menu = False

        else:
            running_destination_selection = True

            source = services.get(main_menu._menu_entries[main_selection])()

            while running_destination_selection:
                destination_selection = destination_menu.show()

                if destination_selection == len(destination_menu._menu_entries)-1 or destination_selection == None:
                    running_destination_selection = False

                elif destination_selection == len(destination_menu._menu_entries)-2:
                    destination = YoutubeMusic()
                    local_download = True

                else:
                    destination = services.get(destination_menu._menu_entries[destination_selection])()

                running_destination_selection = False
                running_main_menu = False

    if local_download:
        download_tracks()

    else:
        print(f'Syncing liked tracks from {source.get_service_name()} to {destination.get_service_name()}')
        transfer_likes(source, destination)




def create_menu(title, items):
    cursor = "> "
    cursor_style = ("fg_red", "bold")
    menu_style = ("bg_red", "fg_yellow")

    return TerminalMenu(
        menu_entries = items,
        title = make_title_string(title),
        menu_cursor = cursor,
        menu_cursor_style = cursor_style,
        menu_highlight_style = menu_style,
        cycle_cursor = True,
        clear_screen = True)

def get_app_title():
    return """
            .-.   .-. .----. .----..----. 
            |  `.'  |{ {__  { {__  | {}  }
            | |\ /| |.-._} }.-._} }| .--' 
            `-' ` `-'`----' `----' `-'    
            """

def download_tracks():
    limit = 100

    menu_title = 'MSPS uses yt-dlp to download your tracks from the Youtube Music database.' \
                f'\nIt is about to import your liked songs from {source.get_service_name()}.' \
                f'\nHow many would you like to be downloaded (approximate number, the api tends to just do its thing)? Press Esc for default value of {limit}.'
    menu_items = {'10': 10,
                '50': 50,
                '100': 100,
                '200': 200,
                '1000': 1000,
                'all': 1000000}

    menu = create_menu(menu_title, list(menu_items))
    running = True

    selection = menu.show()
    limit = menu_items.get(str(menu._menu_entries[selection]))

    liked_tracks = source.get_liked_tracks(limit=limit)

    print(f'Downloading {len(liked_tracks)} tracks...')

    for track in liked_tracks:
        destination.download_track(track)

def transfer_likes(source: StreamingService, destination: StreamingService):
    liked_tracks = source.get_liked_tracks()

    for track in progressbar(liked_tracks, 'Liking Tracks'):
        destination.like_track(track)

def make_title_string(title: str):
    return get_app_title() + f'\n{title}'

if __name__ == '__main__':
    print(get_app_title())
    main()
