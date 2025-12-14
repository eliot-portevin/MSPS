from utils.cli_functions import *
from utils.menu import Menu
from services.Spotify import Spotify
from services.YoutubeMusic import YoutubeMusic
from streaming_service import StreamingService
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

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


# Download tracks locally using multiple threads. Each thread has its own YoutubeMusic instance to avoid synchronisation
# issues. The lowest of 8 or (2 * CPU cores) threads is used.

def _prompt_download_limit(source: StreamingService):
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
        return None

    return items.get(selection[0])


# Worker function for downloading a single track, used by {_run_downloads}
def _worker(track, thread_local):
    os.makedirs(os.path.join(os.getcwd(), 'Downloads'), exist_ok=True)  # Ensure Downloads directory exists

    # Get or create thread-local YoutubeMusic instance
    dest = getattr(thread_local, 'destination', None)
    if dest is None:
        dest = YoutubeMusic()
        thread_local.destination = dest

    try:
        return dest.download_track(track)
    except Exception as e:
        try:
            dest.LOGGER.log(f'Error downloading {track.get_title()} - {track.get_artist()}: {e}')
        except Exception:
            print(f'Error downloading {track.get_title()} - {track.get_artist()}: {e}')
        return False


# Run the downloads using a thread pool and track progress
def _run_downloads(tracks, max_workers):
    thread_local = threading.local()

    downloaded = 0
    total = len(tracks)

    print(f'Starting downloads with {max_workers} worker(s). Attempting {total} track(s).')

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_worker, track, thread_local): track for track in tracks}

        for future in as_completed(futures):
            try:
                success = future.result()
                if success:
                    downloaded += 1
            except Exception as e:
                track = futures.get(future)
                print(f'Unhandled error downloading {track.get_title() if track else "<unknown>"}: {e}')

            print(f'Downloaded {downloaded}/{total} (attempted {len([f for f in futures if f.done()])})', end='\r')

    return downloaded, total


# High-level orchestration for downloading liked tracks
def download_tracks(source: StreamingService):
    limit = _prompt_download_limit(source)
    if limit is None:
        return

    tracks = source.get_liked_tracks(limit=limit)  # Limit is just a suggestion to the API, may return more

    if not tracks:
        print('No tracks found to download.')
        return

    max_workers = os.cpu_count() * 2 if os.cpu_count() else 4

    downloaded, total = _run_downloads(tracks, max_workers)

    print(f"\nFinished. Successfully downloaded {downloaded}/{total} track(s).")


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
