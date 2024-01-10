class Track():

    def __init__(self, title, artist, album, duration):
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration

    def get_title(self):
        # Return title or else empty string
        return self.title if self.title is not None else ''

    def get_artist(self):
        return self.artist if self.artist is not None else ''

    def get_album(self):
        return self.album if self.album is not None else ''

    def get_duration_in_seconds(self):
        return self.duration if self.duration is not None else 0
