from flask import Flask, jsonify, request
import csv
import os
import webbrowser
import threading
from SQL.database_models import Movie, Link, Rating, Tag, get_session, create_tables

app = Flask(__name__)

def get_csv_path(filename):
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'database', filename)
    if os.path.exists(downloads_path):
        return downloads_path
    return filename

def load_data_to_database():
    print("Tworzenie tabel...")
    create_tables()
    print("Tabele utworzone\n")
    
    session = get_session()
    
    print("Ładowanie filmów...")
    csv_path = get_csv_path('movies.csv')
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
    for encoding in encodings:
        try:
            with open(csv_path, newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    movie = Movie(
                        movie_id=int(row['movieId']),
                        title=row['title'],
                        genres=row['genres']
                    )
                    session.merge(movie)
                    count += 1
                    if count % 1000 == 0:
                        session.commit()
                session.commit()
                print(f"Załadowano {count} filmów")
            break
        except Exception as e:
            continue
    
    print("Ładowanie linków")
    csv_path = get_csv_path('links.csv')
    for encoding in encodings:
        try:
            with open(csv_path, newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    link = Link(
                        movie_id=int(row['movieId']),
                        imdb_id=row['imdbId'],
                        tmdb_id=row['tmdbId']
                    )
                    session.merge(link)
                    count += 1
                    if count % 1000 == 0:
                        session.commit()
                session.commit()
                print(f"Załadowano {count} linków")
            break
        except Exception as e:
            continue
    
    print("Ładowanie ocen")
    csv_path = get_csv_path('ratings.csv')
    for encoding in encodings:
        try:
            with open(csv_path, newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    rating = Rating(
                        user_id=int(row['userId']),
                        movie_id=int(row['movieId']),
                        rating=float(row['rating']),
                        timestamp=int(row['timestamp'])
                    )
                    session.add(rating)
                    count += 1
                    if count % 10000 == 0:
                        session.commit()
                session.commit()
                print(f"Załadowano {count} ocen")
            break
        except Exception as e:
            continue
    
    print("Ładowanie tagów")
    csv_path = get_csv_path('tags.csv')
    for encoding in encodings:
        try:
            with open(csv_path, newline='', encoding=encoding) as csvfile:
                reader = csv.DictReader(csvfile)
                count = 0
                for row in reader:
                    tag = Tag(
                        user_id=int(row['userId']),
                        movie_id=int(row['movieId']),
                        tag=row['tag'],
                        timestamp=int(row['timestamp'])
                    )
                    session.add(tag)
                    count += 1
                    if count % 1000 == 0:
                        session.commit()
                session.commit()
                print(f"Załadowano {count} tagów")
            break
        except Exception as e:
            continue
    
    session.close()
    print("\nWszystkie dane zostały załadowane do bazy!")

@app.route('/movies')
def get_movies():
    session = get_session()
    try:
        movies = session.query(Movie).all()
        result = [{'movie_id': m.movie_id, 'title': m.title, 'genres': m.genres} for m in movies]
        return jsonify(result)
    finally:
        session.close()

@app.route('/movies/<int:movie_id>', methods=['GET'])
def get_movie(movie_id):
    session = get_session()
    try:
        movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        return jsonify({'movie_id': movie.movie_id, 'title': movie.title, 'genres': movie.genres})
    finally:
        session.close()

@app.route('/movies', methods=['POST'])
def create_movie():
    session = get_session()
    try:
        data = request.get_json()
        if not data or 'movie_id' not in data or 'title' not in data:
            return jsonify({'error': 'Missing required fields: movie_id, title'}), 400
        
        existing = session.query(Movie).filter(Movie.movie_id == data['movie_id']).first()
        if existing:
            return jsonify({'error': 'Movie with this ID already exists'}), 400
        
        movie = Movie(
            movie_id=data['movie_id'],
            title=data['title'],
            genres=data.get('genres', '')
        )
        session.add(movie)
        session.commit()
        return jsonify({'movie_id': movie.movie_id, 'title': movie.title, 'genres': movie.genres}), 201
    finally:
        session.close()

@app.route('/movies/<int:movie_id>', methods=['PUT'])
def update_movie(movie_id):
    session = get_session()
    try:
        movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        
        data = request.get_json()
        if 'title' in data:
            movie.title = data['title']
        if 'genres' in data:
            movie.genres = data['genres']
        
        session.commit()
        return jsonify({'movie_id': movie.movie_id, 'title': movie.title, 'genres': movie.genres})
    finally:
        session.close()

@app.route('/movies/<int:movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
    session = get_session()
    try:
        movie = session.query(Movie).filter(Movie.movie_id == movie_id).first()
        if movie is None:
            return jsonify({'error': 'Movie not found'}), 404
        
        session.delete(movie)
        session.commit()
        return jsonify({'message': 'Movie deleted successfully'}), 200
    finally:
        session.close()

@app.route('/links')
def get_links():
    session = get_session()
    try:
        links = session.query(Link).all()
        result = [{'movie_id': l.movie_id, 'imdb_id': l.imdb_id, 'tmdb_id': l.tmdb_id} for l in links]
        return jsonify(result)
    finally:
        session.close()

@app.route('/links/<int:movie_id>', methods=['GET'])
def get_link(movie_id):
    session = get_session()
    try:
        link = session.query(Link).filter(Link.movie_id == movie_id).first()
        if link is None:
            return jsonify({'error': 'Link not found'}), 404
        return jsonify({'movie_id': link.movie_id, 'imdb_id': link.imdb_id, 'tmdb_id': link.tmdb_id})
    finally:
        session.close()

@app.route('/links', methods=['POST'])
def create_link():
    session = get_session()
    try:
        data = request.get_json()
        if not data or 'movie_id' not in data:
            return jsonify({'error': 'Missing required field: movie_id'}), 400
        
        existing = session.query(Link).filter(Link.movie_id == data['movie_id']).first()
        if existing:
            return jsonify({'error': 'Link with this movie_id already exists'}), 400
        
        link = Link(
            movie_id=data['movie_id'],
            imdb_id=data.get('imdb_id', ''),
            tmdb_id=data.get('tmdb_id', '')
        )
        session.add(link)
        session.commit()
        return jsonify({'movie_id': link.movie_id, 'imdb_id': link.imdb_id, 'tmdb_id': link.tmdb_id}), 201
    finally:
        session.close()

@app.route('/links/<int:movie_id>', methods=['PUT'])
def update_link(movie_id):
    session = get_session()
    try:
        link = session.query(Link).filter(Link.movie_id == movie_id).first()
        if link is None:
            return jsonify({'error': 'Link not found'}), 404
        
        data = request.get_json()
        if 'imdb_id' in data:
            link.imdb_id = data['imdb_id']
        if 'tmdb_id' in data:
            link.tmdb_id = data['tmdb_id']
        
        session.commit()
        return jsonify({'movie_id': link.movie_id, 'imdb_id': link.imdb_id, 'tmdb_id': link.tmdb_id})
    finally:
        session.close()

@app.route('/links/<int:movie_id>', methods=['DELETE'])
def delete_link(movie_id):
    session = get_session()
    try:
        link = session.query(Link).filter(Link.movie_id == movie_id).first()
        if link is None:
            return jsonify({'error': 'Link not found'}), 404
        
        session.delete(link)
        session.commit()
        return jsonify({'message': 'Link deleted successfully'}), 200
    finally:
        session.close()

@app.route('/ratings')
def get_ratings():
    session = get_session()
    try:
        ratings = session.query(Rating).all()
        result = [{'id': r.id, 'user_id': r.user_id, 'movie_id': r.movie_id, 'rating': r.rating, 'timestamp': r.timestamp} for r in ratings]
        return jsonify(result)
    finally:
        session.close()

@app.route('/ratings/<int:rating_id>', methods=['GET'])
def get_rating(rating_id):
    session = get_session()
    try:
        rating = session.query(Rating).filter(Rating.id == rating_id).first()
        if rating is None:
            return jsonify({'error': 'Rating not found'}), 404
        return jsonify({'id': rating.id, 'user_id': rating.user_id, 'movie_id': rating.movie_id, 
                       'rating': rating.rating, 'timestamp': rating.timestamp})
    finally:
        session.close()

@app.route('/ratings', methods=['POST'])
def create_rating():
    session = get_session()
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'movie_id' not in data or 'rating' not in data:
            return jsonify({'error': 'Missing required fields: user_id, movie_id, rating'}), 400
        
        rating = Rating(
            user_id=data['user_id'],
            movie_id=data['movie_id'],
            rating=data['rating'],
            timestamp=data.get('timestamp', 0)
        )
        session.add(rating)
        session.commit()
        return jsonify({'id': rating.id, 'user_id': rating.user_id, 'movie_id': rating.movie_id, 
                       'rating': rating.rating, 'timestamp': rating.timestamp}), 201
    finally:
        session.close()

@app.route('/ratings/<int:rating_id>', methods=['PUT'])
def update_rating(rating_id):
    session = get_session()
    try:
        rating = session.query(Rating).filter(Rating.id == rating_id).first()
        if rating is None:
            return jsonify({'error': 'Rating not found'}), 404
        
        data = request.get_json()
        if 'user_id' in data:
            rating.user_id = data['user_id']
        if 'movie_id' in data:
            rating.movie_id = data['movie_id']
        if 'rating' in data:
            rating.rating = data['rating']
        if 'timestamp' in data:
            rating.timestamp = data['timestamp']
        
        session.commit()
        return jsonify({'id': rating.id, 'user_id': rating.user_id, 'movie_id': rating.movie_id, 
                       'rating': rating.rating, 'timestamp': rating.timestamp})
    finally:
        session.close()

@app.route('/ratings/<int:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
    session = get_session()
    try:
        rating = session.query(Rating).filter(Rating.id == rating_id).first()
        if rating is None:
            return jsonify({'error': 'Rating not found'}), 404
        
        session.delete(rating)
        session.commit()
        return jsonify({'message': 'Rating deleted successfully'}), 200
    finally:
        session.close()

@app.route('/tags')
def get_tags():
    session = get_session()
    try:
        tags = session.query(Tag).all()
        result = [{'id': t.id, 'user_id': t.user_id, 'movie_id': t.movie_id, 'tag': t.tag, 'timestamp': t.timestamp} for t in tags]
        return jsonify(result)
    finally:
        session.close()

@app.route('/tags/<int:tag_id>', methods=['GET'])
def get_tag(tag_id):
    session = get_session()
    try:
        tag = session.query(Tag).filter(Tag.id == tag_id).first()
        if tag is None:
            return jsonify({'error': 'Tag not found'}), 404
        return jsonify({'id': tag.id, 'user_id': tag.user_id, 'movie_id': tag.movie_id, 
                       'tag': tag.tag, 'timestamp': tag.timestamp})
    finally:
        session.close()

@app.route('/tags', methods=['POST'])
def create_tag():
    session = get_session()
    try:
        data = request.get_json()
        if not data or 'user_id' not in data or 'movie_id' not in data or 'tag' not in data:
            return jsonify({'error': 'Missing required fields: user_id, movie_id, tag'}), 400
        
        tag = Tag(
            user_id=data['user_id'],
            movie_id=data['movie_id'],
            tag=data['tag'],
            timestamp=data.get('timestamp', 0)
        )
        session.add(tag)
        session.commit()
        return jsonify({'id': tag.id, 'user_id': tag.user_id, 'movie_id': tag.movie_id, 
                       'tag': tag.tag, 'timestamp': tag.timestamp}), 201
    finally:
        session.close()

@app.route('/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
    session = get_session()
    try:
        tag = session.query(Tag).filter(Tag.id == tag_id).first()
        if tag is None:
            return jsonify({'error': 'Tag not found'}), 404
        
        data = request.get_json()
        if 'user_id' in data:
            tag.user_id = data['user_id']
        if 'movie_id' in data:
            tag.movie_id = data['movie_id']
        if 'tag' in data:
            tag.tag = data['tag']
        if 'timestamp' in data:
            tag.timestamp = data['timestamp']
        
        session.commit()
        return jsonify({'id': tag.id, 'user_id': tag.user_id, 'movie_id': tag.movie_id, 
                       'tag': tag.tag, 'timestamp': tag.timestamp})
    finally:
        session.close()

@app.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
    session = get_session()
    try:
        tag = session.query(Tag).filter(Tag.id == tag_id).first()
        if tag is None:
            return jsonify({'error': 'Tag not found'}), 404
        
        session.delete(tag)
        session.commit()
        return jsonify({'message': 'Tag deleted successfully'}), 200
    finally:
        session.close()

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/movies')

if __name__ == '__main__':
    db_path = os.path.join('SQL', 'movies.db')
    if not os.path.exists(db_path):
        print("Baza danych nie istnieje. Ładowanie danych...")
        load_data_to_database()
    
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True)

