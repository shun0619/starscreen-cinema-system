"""
Data Access - Movies  [M3]
Reads come from the in-memory objects (loaded from SQL Server or the
sample data). Every change is also written through to the database
when it is enabled -- these persist functions are no-ops otherwise.
"""
from store import MOVIES, GENRES
from database import db


def get_all():
    return MOVIES


def next_id():
    return f"MV-{len(MOVIES) + 1:02d}"


def get_genres():
    return GENRES


def persist_new(movie):
    """INSERT a movie the Manager just added (the object itself is
    appended to the catalogue list by Manager.add_movie)."""
    if db.enabled():
        db.execute(
            "INSERT INTO MOVIE (movie_id, title, genre, duration_min, "
            "rating, is_active) VALUES (?, ?, ?, ?, ?, ?)",
            (movie.movie_id, movie.title, movie.genre, movie.duration_min,
             movie.rating, int(movie.is_active)))


def save(movie):
    """UPDATE after an edit / deactivate / restore."""
    if db.enabled():
        db.execute(
            "UPDATE MOVIE SET title = ?, genre = ?, duration_min = ?, "
            "rating = ?, is_active = ? WHERE movie_id = ?",
            (movie.title, movie.genre, movie.duration_min, movie.rating,
             int(movie.is_active), movie.movie_id))
