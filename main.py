from cli_functions import *
from menu import Menu
from services.Spotify import Spotify
from services.YoutubeMusic import YoutubeMusic
from streaming_service import StreamingService

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
    title = "Music Streaming Platform Synchronizer" \
            "\n[Q]/[Esc] to Quit | Navigate with [J, K] or arrow keys, [Enter] to Confirm" \
            "\nSelect the platform to import from:" \
            "\n"
    items = list(services.keys())

    menu = Menu(title=title,
                items=items,
                exit_option=True)

    running = True

    while running:
        selection = menu.get_selection()[0]

        if menu.has_requested_return(selection):
            running = False

        else:
            source = services.get(selection)()

            run_menu_destination(
                {key: services[key] for key in services if key != selection},
                source)


# Menu responsible for determining which platform tracks will be exported to (includes downloading locally)
def run_menu_destination(services, source: StreamingService):
    download_locally_string = 'Download locally'
    title = 'Which platform would you like to export to?'
    items = list(services.keys()) + [download_locally_string]

    menu = Menu(title=title,
                items=items)

    running = True

    while running:
        selection = menu.get_selection()[0]

        if menu.has_requested_return(selection):
            running = False

        elif selection == download_locally_string:
            download_tracks(source)
            running = False

        else:
            destination = services.get(selection)()

            run_menu_transfer_content(source, destination)

            running = False


# Menu responsible for determining what playlists are to be imported: liked tracks, playlists, etc.
def run_menu_transfer_content(source: StreamingService, destination: StreamingService):
    playlists = source.get_all_playlist_names()

    title = f'What would you like to import from {source.get_service_name()} to {destination.get_service_name()}?' \
            '\nPress Space or Tab to select multiple items. Press Enter to confirm.'
    items = ['Liked Tracks'] + playlists

    menu = Menu(title, items, multi_select=True)

    running = True

    while running:
        selection = menu.get_selection()

        if menu.has_requested_return(selection):
            running = False

        else:
            if items.index('Liked Tracks') in selection:
                transfer_likes(source, destination)
                selection.remove(items.index('Liked Tracks'))
            if len(selection) > 0:
                transfer_playlists(source, destination, [items[i] for i in selection])

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

    menu = Menu(title, list(items))
    selection = menu.get_selection()

    if menu.has_requested_return(selection):
        return

    else:
        limit = items.get(selection[0])

    tracks = source.get_liked_tracks(limit=limit)
    destination = YoutubeMusic()

    for track in tracks:
        if limit == 0:
            break

        success = destination.download_track(track)

        if success:
            limit -= 1


def transfer_likes(source: StreamingService, destination: StreamingService):
    liked_tracks = source.get_liked_tracks()

    for track in progressbar(liked_tracks, 'Liking Tracks'):
        destination.like_track(track)


def transfer_playlists(source: StreamingService, destination: StreamingService, playlist_names: list):
    for playlist in playlist_names:
        tracks = source.get_tracks_in_playlist(playlist)

        destination.create_playlist(playlist)
        tracks_in_destination = destination.get_tracks_in_playlist(playlist)

        for track in progressbar(tracks, f'Importing {playlist}'):
            # Check if a similar track is already in the destination playlist
            similar_track_present = any(track.is_similar(dest_track) for dest_track in tracks_in_destination)

            if not similar_track_present:
                destination.add_track_to_playlist(playlist, track)


if __name__ == '__main__':
    main()
