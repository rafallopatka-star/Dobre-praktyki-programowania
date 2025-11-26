import pytest
import sys
import os


sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from api_sql_lite import app
from SQL.database_models import Movie, Link, Rating, Tag, get_session, create_tables, Base, get_engine


@pytest.fixture
def client():
    
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def setup_test_database():
    
    
    create_tables()
    
    
    session = get_session()
    
    
    session.query(Tag).delete()
    session.query(Rating).delete()
    session.query(Link).delete()
    session.query(Movie).delete()
    session.commit()
    
    
    movies = [
        Movie(movie_id=1, title='Test Movie 1', genres='Action|Adventure'),
        Movie(movie_id=2, title='Test Movie 2', genres='Comedy|Drama'),
        Movie(movie_id=3, title='Test Movie 3', genres='Sci-Fi'),
    ]
    for movie in movies:
        session.add(movie)
    
    
    links = [
        Link(movie_id=1, imdb_id='tt0111161', tmdb_id='111'),
        Link(movie_id=2, imdb_id='tt0068646', tmdb_id='222'),
    ]
    for link in links:
        session.add(link)
    
    
    ratings = [
        Rating(user_id=1, movie_id=1, rating=4.5, timestamp=1234567890),
        Rating(user_id=1, movie_id=2, rating=3.5, timestamp=1234567891),
        Rating(user_id=2, movie_id=1, rating=5.0, timestamp=1234567892),
    ]
    for rating in ratings:
        session.add(rating)
    
    
    tags = [
        Tag(user_id=1, movie_id=1, tag='classic', timestamp=1234567890),
        Tag(user_id=1, movie_id=2, tag='funny', timestamp=1234567891),
    ]
    for tag in tags:
        session.add(tag)
    
    session.commit()
    session.close()
    
    yield
    
    
    session = get_session()
    session.query(Tag).delete()
    session.query(Rating).delete()
    session.query(Link).delete()
    session.query(Movie).delete()
    session.commit()
    session.close()


# =====================================================
# TESTY DLA MOVIES
# =====================================================

def test_get_movies_list(client, setup_test_database):
    
    response = client.get('/movies')
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert data[0]['title'] == 'Test Movie 1'
    assert 'movie_id' in data[0]
    assert 'genres' in data[0]


def test_get_movie_by_id(client, setup_test_database):
    
    response = client.get('/movies/1')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['movie_id'] == 1
    assert data['title'] == 'Test Movie 1'
    assert data['genres'] == 'Action|Adventure'


def test_get_movie_not_found(client, setup_test_database):
    
    response = client.get('/movies/99999')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data
    assert data['error'] == 'Movie not found'


def test_create_movie(client, setup_test_database):
    
    new_movie = {
        'movie_id': 100,
        'title': 'New Test Movie',
        'genres': 'Horror|Thriller'
    }
    
    response = client.post('/movies', json=new_movie)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['movie_id'] == 100
    assert data['title'] == 'New Test Movie'
    assert data['genres'] == 'Horror|Thriller'
    
    # Weryfikacja czy film został dodany do bazy
    session = get_session()
    movie = session.query(Movie).filter(Movie.movie_id == 100).first()
    assert movie is not None
    assert movie.title == 'New Test Movie'
    session.close()


def test_create_movie_duplicate(client, setup_test_database):
   
    duplicate_movie = {
        'movie_id': 1,
        'title': 'Duplicate Movie',
        'genres': 'Drama'
    }
    
    response = client.post('/movies', json=duplicate_movie)
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_update_movie(client, setup_test_database):
    
    updated_data = {
        'title': 'Updated Movie Title',
        'genres': 'Documentary'
    }
    
    response = client.put('/movies/1', json=updated_data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['title'] == 'Updated Movie Title'
    assert data['genres'] == 'Documentary'
    
    # Weryfikacja czy zmiana została zapisana w bazie
    session = get_session()
    movie = session.query(Movie).filter(Movie.movie_id == 1).first()
    assert movie.title == 'Updated Movie Title'
    assert movie.genres == 'Documentary'
    session.close()


def test_update_movie_not_found(client, setup_test_database):
    
    response = client.put('/movies/99999', json={'title': 'Test'})
    
    assert response.status_code == 404


def test_delete_movie(client, setup_test_database):
    
    response = client.delete('/movies/3')
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    
    # Weryfikacja czy film został usunięty z bazy
    session = get_session()
    movie = session.query(Movie).filter(Movie.movie_id == 3).first()
    assert movie is None
    session.close()


def test_delete_movie_not_found(client, setup_test_database):
    
    response = client.delete('/movies/99999')
    
    assert response.status_code == 404


# =====================================================
# TESTY DLA LINKS
# =====================================================

def test_get_links_list(client, setup_test_database):
    
    response = client.get('/links')
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert 'movie_id' in data[0]
    assert 'imdb_id' in data[0]
    assert 'tmdb_id' in data[0]


def test_get_link_by_id(client, setup_test_database):
   
    response = client.get('/links/1')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['movie_id'] == 1
    assert data['imdb_id'] == 'tt0111161'
    assert data['tmdb_id'] == '111'


def test_get_link_not_found(client, setup_test_database):
    
    response = client.get('/links/99999')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


def test_create_link(client, setup_test_database):
    
    new_link = {
        'movie_id': 3,
        'imdb_id': 'tt0071562',
        'tmdb_id': '333'
    }
    
    response = client.post('/links', json=new_link)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['movie_id'] == 3
    assert data['imdb_id'] == 'tt0071562'
    
    # Weryfikacja w bazie
    session = get_session()
    link = session.query(Link).filter(Link.movie_id == 3).first()
    assert link is not None
    assert link.imdb_id == 'tt0071562'
    session.close()


def test_create_link_duplicate(client, setup_test_database):
   
    duplicate_link = {
        'movie_id': 1,
        'imdb_id': 'tt9999999',
        'tmdb_id': '999'
    }
    
    response = client.post('/links', json=duplicate_link)
    
    assert response.status_code == 400


def test_update_link(client, setup_test_database):
    
    updated_data = {
        'imdb_id': 'tt0000000',
        'tmdb_id': '000'
    }
    
    response = client.put('/links/1', json=updated_data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['imdb_id'] == 'tt0000000'
    assert data['tmdb_id'] == '000'
    
    # Weryfikacja w bazie
    session = get_session()
    link = session.query(Link).filter(Link.movie_id == 1).first()
    assert link.imdb_id == 'tt0000000'
    session.close()


def test_update_link_not_found(client, setup_test_database):
    
    response = client.put('/links/99999', json={'imdb_id': 'test'})
    
    assert response.status_code == 404


def test_delete_link(client, setup_test_database):
    
    response = client.delete('/links/2')
    
    assert response.status_code == 200
    
    # Weryfikacja w bazie
    session = get_session()
    link = session.query(Link).filter(Link.movie_id == 2).first()
    assert link is None
    session.close()


def test_delete_link_not_found(client, setup_test_database):
    
    response = client.delete('/links/99999')
    
    assert response.status_code == 404


# =====================================================
# TESTY DLA RATINGS
# =====================================================

def test_get_ratings_list(client, setup_test_database):
    
    response = client.get('/ratings')
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 3
    assert 'id' in data[0]
    assert 'user_id' in data[0]
    assert 'movie_id' in data[0]
    assert 'rating' in data[0]


def test_get_rating_by_id(client, setup_test_database):
    
    # Pobierz ID pierwszej oceny
    session = get_session()
    rating = session.query(Rating).first()
    rating_id = rating.id
    session.close()
    
    response = client.get(f'/ratings/{rating_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == rating_id
    assert 'user_id' in data
    assert 'rating' in data


def test_get_rating_not_found(client, setup_test_database):
    
    response = client.get('/ratings/99999')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


def test_create_rating(client, setup_test_database):
    
    new_rating = {
        'user_id': 3,
        'movie_id': 2,
        'rating': 4.0,
        'timestamp': 1234567900
    }
    
    response = client.post('/ratings', json=new_rating)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['user_id'] == 3
    assert data['movie_id'] == 2
    assert data['rating'] == 4.0
    assert 'id' in data
    
    # Weryfikacja w bazie
    session = get_session()
    ratings_count = session.query(Rating).filter(Rating.user_id == 3).count()
    assert ratings_count == 1
    session.close()


def test_create_rating_missing_fields(client, setup_test_database):
    
    incomplete_rating = {
        'user_id': 3
    }
    
    response = client.post('/ratings', json=incomplete_rating)
    
    assert response.status_code == 400


def test_update_rating(client, setup_test_database):
    
    session = get_session()
    rating = session.query(Rating).first()
    rating_id = rating.id
    session.close()
    
    updated_data = {
        'rating': 5.0,
        'timestamp': 9999999999
    }
    
    response = client.put(f'/ratings/{rating_id}', json=updated_data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['rating'] == 5.0
    assert data['timestamp'] == 9999999999
    
    # Weryfikacja w bazie
    session = get_session()
    rating = session.query(Rating).filter(Rating.id == rating_id).first()
    assert rating.rating == 5.0
    session.close()


def test_update_rating_not_found(client, setup_test_database):
    
    response = client.put('/ratings/99999', json={'rating': 5.0})
    
    assert response.status_code == 404


def test_delete_rating(client, setup_test_database):
    
    session = get_session()
    rating = session.query(Rating).first()
    rating_id = rating.id
    session.close()
    
    response = client.delete(f'/ratings/{rating_id}')
    
    assert response.status_code == 200
    
    # Weryfikacja w bazie
    session = get_session()
    rating = session.query(Rating).filter(Rating.id == rating_id).first()
    assert rating is None
    session.close()


def test_delete_rating_not_found(client, setup_test_database):
   
    response = client.delete('/ratings/99999')
    
    assert response.status_code == 404


# =====================================================
# TESTY DLA TAGS
# =====================================================

def test_get_tags_list(client, setup_test_database):
   
    response = client.get('/tags')
    
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert 'id' in data[0]
    assert 'user_id' in data[0]
    assert 'movie_id' in data[0]
    assert 'tag' in data[0]


def test_get_tag_by_id(client, setup_test_database):
   
    session = get_session()
    tag = session.query(Tag).first()
    tag_id = tag.id
    session.close()
    
    response = client.get(f'/tags/{tag_id}')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['id'] == tag_id
    assert 'tag' in data
    assert 'user_id' in data


def test_get_tag_not_found(client, setup_test_database):
    
    response = client.get('/tags/99999')
    
    assert response.status_code == 404
    data = response.get_json()
    assert 'error' in data


def test_create_tag(client, setup_test_database):
   
    new_tag = {
        'user_id': 2,
        'movie_id': 3,
        'tag': 'exciting',
        'timestamp': 1234567950
    }
    
    response = client.post('/tags', json=new_tag)
    
    assert response.status_code == 201
    data = response.get_json()
    assert data['user_id'] == 2
    assert data['movie_id'] == 3
    assert data['tag'] == 'exciting'
    assert 'id' in data
    
    # Weryfikacja w bazie
    session = get_session()
    tags_count = session.query(Tag).filter(Tag.tag == 'exciting').count()
    assert tags_count == 1
    session.close()


def test_create_tag_missing_fields(client, setup_test_database):
    
    incomplete_tag = {
        'user_id': 2
    }
    
    response = client.post('/tags', json=incomplete_tag)
    
    assert response.status_code == 400


def test_update_tag(client, setup_test_database):
    
    session = get_session()
    tag = session.query(Tag).first()
    tag_id = tag.id
    session.close()
    
    updated_data = {
        'tag': 'updated-tag',
        'timestamp': 8888888888
    }
    
    response = client.put(f'/tags/{tag_id}', json=updated_data)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['tag'] == 'updated-tag'
    assert data['timestamp'] == 8888888888
    
    # Weryfikacja w bazie
    session = get_session()
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    assert tag.tag == 'updated-tag'
    session.close()


def test_update_tag_not_found(client, setup_test_database):
    
    response = client.put('/tags/99999', json={'tag': 'test'})
    
    assert response.status_code == 404


def test_delete_tag(client, setup_test_database):
    
    session = get_session()
    tag = session.query(Tag).first()
    tag_id = tag.id
    session.close()
    
    response = client.delete(f'/tags/{tag_id}')
    
    assert response.status_code == 200
    
    # Weryfikacja w bazie
    session = get_session()
    tag = session.query(Tag).filter(Tag.id == tag_id).first()
    assert tag is None
    session.close()


def test_delete_tag_not_found(client, setup_test_database):
    
    response = client.delete('/tags/99999')
    
    assert response.status_code == 404
