from argparse import ArgumentParser

from services.Spotify import Spotify
from services.YoutubeMusic import YoutubeMusic


'''
See https://colab.research.google.com/github/rruff82/misc/blob/main/YTM2Spotify_clean.ipynb#scrollTo=ehOBPh0NrZmE
for detailed explanations. The authentification process was copied from there.
'''


def main():
    parser = ArgumentParser(description='Synchronise your music streaming services.')
    parser.add_argument('--source', choices=['yt', 'sp'], help='Source streaming service')
    parser.add_argument('--destination', choices=['yt', 'sp'], help='Destination streaming service')

    args = parser.parse_args()

    if args.source and args.destination:
        switch = {
            'yt': YoutubeMusic(),
            'sp': Spotify()
        }

        source = switch.get(args.source)
        destination = switch.get(args.destination)

        liked_tracks = source.get_liked_tracks(limit=10)
        for track in liked_tracks:
            destination.like_track(track)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
