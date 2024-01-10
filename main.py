from services.Spotify import Spotify
from services.YoutubeMusic import YoutubeMusic


def main():
    youtube_music = YoutubeMusic()
    spotify = Spotify()

    likes = youtube_music.get_liked_tracks(limit=50)

    for track in likes:
        spotify.like_track(track)


if __name__ == '__main__':
    main()
