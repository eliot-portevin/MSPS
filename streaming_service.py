from abc import ABC, abstractmethod

from logger import Logger
from Track import Track


class StreamingService(ABC):

    def __init__(self):
        self.LOGGER = Logger()
        self.ignored_playlists = ['Liked Songs', 'Liked Music', 'Episodes for Later']

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def get_all_playlist_names(self):
        pass

    @abstractmethod
    def get_liked_tracks(self, limit: int = 1000000):
        pass

    @abstractmethod
    def get_tracks_in_playlist(self, playlist_name: str):
        pass

    @abstractmethod
    def add_track_to_playlist(self, playlist_name: str, track: Track):
        pass

    @abstractmethod
    def like_track(self, track: Track):
        pass

    @abstractmethod
    def get_service_name(self):
        pass

    @abstractmethod
    def create_playlist(self, playlist):
        pass