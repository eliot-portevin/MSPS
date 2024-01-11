from fuzzywuzzy import fuzz


class Track():

    def __init__(self, title, artist, album, duration):
        self.title = title
        self.artist = artist
        self.album = album
        self.duration = duration

    def __eq__(self, other):
        if not isinstance(other, Track):
            return False
        return self.get_title() == other.get_title() and self.get_artist() == other.get_artist()

    def is_similar(self, track2):
        title_similarity = fuzz.token_sort_ratio(self.title, track2.title)
        artist_similarity = fuzz.token_sort_ratio(self.artist, track2.artist)
        album_similarity = fuzz.token_sort_ratio(self.album, track2.album)

        # Combine the similarities based on weights or priorities
        overall_similarity = (
                0.4 * title_similarity +
                0.4 * artist_similarity +
                0.2 * album_similarity)

        return overall_similarity > 70


    def get_title(self):
        # Return title or else empty string
        return self.title if self.title is not None else ''

    def get_artist(self):
        return self.artist if self.artist is not None else ''

    def get_album(self):
        return self.album if self.album is not None else ''

    def get_duration_in_seconds(self):
        return self.duration if self.duration is not None else 0
