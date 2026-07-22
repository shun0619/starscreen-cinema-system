"""
M3 - Movies & screenings.

TC-03: a Manager can add a movie; it appears in the catalogue, active.
"""

from business_logic import auth_service, movie_service


def test_manager_can_add_movie():
    manager = auth_service.login("manager", "manager123")
    before = len(movie_service.list_movies())

    movie = movie_service.add_movie(manager, "QA Test Feature", "Action", 100, "M")

    assert len(movie_service.list_movies()) == before + 1
    assert movie.is_active is True
    assert movie in movie_service.list_movies(search="QA Test Feature")
