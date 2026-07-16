"""
Business Logic - Movies  [Member 3]
Catalogue changes are Manager-only: enforced through get_permissions()
and delegated to the Manager's own methods.
"""
from data_access import movie_repository
from business_logic.auth_service import require_permission
from models.movie import Movie


def list_movies(genre="All", search="", active_only=False):
    search = (search or "").lower()
    return [
        m for m in movie_repository.get_all()
        if (genre in ("All", "") or m.genre == genre)
        and search in m.title.lower()
        and (m.is_active or not active_only)
    ]


def add_movie(current_user, title, genre, duration_min, rating):
    require_permission(current_user, "catalogue")
    title = (title or "").strip()
    if not title:
        raise ValueError("Title is required.")
    try:
        duration_min = int(duration_min)
    except (TypeError, ValueError):
        raise ValueError("Duration must be a whole number of minutes.")
    movie = Movie(movie_repository.next_id(), title, genre, duration_min,
                  (rating or "").strip())
    current_user.add_movie(movie_repository.get_all(), movie)
    movie_repository.persist_new(movie)   # write-through to SQL Server
    return movie


def edit_movie(current_user, movie, title, genre, duration_min, rating):
    require_permission(current_user, "catalogue")
    title = (title or "").strip()
    if not title:
        raise ValueError("Title is required.")
    try:
        duration_min = int(duration_min)
    except (TypeError, ValueError):
        raise ValueError("Duration must be a whole number of minutes.")
    current_user.update_movie(movie, title=title, genre=genre,
                              duration_min=duration_min,
                              rating=(rating or "").strip())
    movie_repository.save(movie)          # write-through to SQL Server
    return movie


def deactivate_movie(current_user, movie):
    require_permission(current_user, "catalogue")
    current_user.deactivate_movie(movie)
    movie_repository.save(movie)


def restore_movie(current_user, movie):
    require_permission(current_user, "catalogue")
    movie.is_active = True
    movie_repository.save(movie)


def get_genres():
    return movie_repository.get_genres()
