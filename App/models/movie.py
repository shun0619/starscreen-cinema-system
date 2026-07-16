"""
==========================================
Domain Model - Movie  [Member 3]
==========================================
"""


class Movie:

    def __init__(self, movie_id, title, genre, duration_min, rating="", is_active=True):
        self.movie_id = movie_id
        self.title = title
        self.genre = genre               # Action / Drama / Horror / Kids / Romance / Thriller
        self.duration_min = duration_min  # length in minutes
        self.rating = rating
        self.is_active = is_active

    def update_movie(self, **fields):
        """movie.update_movie(genre='Action', ...) -- updates known fields only."""
        for key, value in fields.items():
            if hasattr(self, key):
                setattr(self, key, value)

    @property
    def duration_text(self):
        hours, minutes = divmod(self.duration_min, 60)
        return f"{hours}h {minutes:02d}m"

    @property
    def status(self):
        return "Active" if self.is_active else "Inactive"
