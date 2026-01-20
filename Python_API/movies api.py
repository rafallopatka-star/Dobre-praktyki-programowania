from flask import Flask, jsonify, request
import csv
import os
import webbrowser
import threading

app = Flask(__name__)

# In-memory storage for CRUD operations
movies_data = []
links_data = []
ratings_data = []
tags_data = []

class Movie:
  def __init__(self, movie_id, title, genres):
    self.movie_id = movie_id
    self.title = title
    self.genres = genres

class Link:
  def __init__(self, movie_id, imdb_id, tmdb_id):
    self.movie_id = movie_id
    self.imdb_id = imdb_id
    self.tmdb_id = tmdb_id

class Rating:
  def __init__(self, user_id, movie_id, rating, timestamp):
    self.user_id = user_id
    self.movie_id = movie_id
    self.rating = rating
    self.timestamp = timestamp

class Tag:
  def __init__(self, user_id, movie_id, tag, timestamp):
    self.user_id = user_id
    self.movie_id = movie_id
    self.tag = tag
    self.timestamp = timestamp

def get_csv_path(filename):
  downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'database', filename)
  if os.path.exists(downloads_path):
    return downloads_path
  target_path = filename
  if os.path.exists(target_path):
    return target_path
  return None

@app.route('/movies')
def get_movies():
  global movies_data
  if not movies_data:
    csv_path = get_csv_path('movies.csv')
    movies = []
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
    for encoding in encodings:
      try:
        with open(csv_path, newline='', encoding=encoding) as csvfile:
          reader = csv.DictReader(csvfile)
          for row in reader:
            movie_id = row['movieId']
            title = row['title']
            genres = row['genres']
            movie = Movie(movie_id, title, genres)
            movies.append(movie.__dict__)
        movies_data = movies
        break
      except (UnicodeDecodeError, KeyError) as e:
        if isinstance(e, KeyError):
          print(f"Błąd klucza: {e}, Dostępne klucze: {list(row.keys()) if 'row' in locals() else 'brak'}")
        movies = []
        continue
  return jsonify(movies_data)

@app.route('/movies/<movie_id>', methods=['GET'])
def get_movie(movie_id):
  global movies_data
  if not movies_data:
    get_movies()
  
  movie = next((m for m in movies_data if m['movie_id'] == movie_id), None)
  if movie is None:
    return jsonify({'error': 'Movie not found'}), 404
  return jsonify(movie)

@app.route('/movies', methods=['POST'])
def create_movie():
  global movies_data
  if not movies_data:
    get_movies()
  
  data = request.get_json()
  if not data or 'movie_id' not in data or 'title' not in data:
    return jsonify({'error': 'Missing required fields: movie_id, title'}), 400
  
  existing = next((m for m in movies_data if m['movie_id'] == data['movie_id']), None)
  if existing:
    return jsonify({'error': 'Movie with this ID already exists'}), 400
  
  new_movie = {
    'movie_id': data['movie_id'],
    'title': data['title'],
    'genres': data.get('genres', '')
  }
  movies_data.append(new_movie)
  return jsonify(new_movie), 201

@app.route('/movies/<movie_id>', methods=['PUT'])
def update_movie(movie_id):
  global movies_data
  if not movies_data:
    get_movies()
  
  movie = next((m for m in movies_data if m['movie_id'] == movie_id), None)
  if movie is None:
    return jsonify({'error': 'Movie not found'}), 404
  
  data = request.get_json()
  if 'title' in data:
    movie['title'] = data['title']
  if 'genres' in data:
    movie['genres'] = data['genres']
  
  return jsonify(movie)

@app.route('/movies/<movie_id>', methods=['DELETE'])
def delete_movie(movie_id):
  global movies_data
  if not movies_data:
    get_movies()
  
  movie = next((m for m in movies_data if m['movie_id'] == movie_id), None)
  if movie is None:
    return jsonify({'error': 'Movie not found'}), 404
  
  movies_data.remove(movie)
  return jsonify({'message': 'Movie deleted successfully'}), 200





@app.route('/links')
def get_links():
  global links_data
  if not links_data:
    csv_path = get_csv_path('links.csv')
    links = []
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
    for encoding in encodings:
      try:
        with open(csv_path, newline='', encoding=encoding) as csvfile:
          reader = csv.DictReader(csvfile)
          for row in reader:
            movie_id = row['movieId']
            imdb_id = row['imdbId']
            tmdb_id = row['tmdbId']
            link = Link(movie_id, imdb_id, tmdb_id)
            links.append(link.__dict__)
        links_data = links
        break
      except (UnicodeDecodeError, KeyError) as e:
        links = []
        continue
  return jsonify(links_data)

@app.route('/links/<movie_id>', methods=['GET'])
def get_link(movie_id):
  global links_data
  if not links_data:
    get_links()
  
  link = next((l for l in links_data if l['movie_id'] == movie_id), None)
  if link is None:
    return jsonify({'error': 'Link not found'}), 404
  return jsonify(link)

@app.route('/links', methods=['POST'])
def create_link():
  global links_data
  if not links_data:
    get_links()
  
  data = request.get_json()
  if not data or 'movie_id' not in data:
    return jsonify({'error': 'Missing required field: movie_id'}), 400
  
  existing = next((l for l in links_data if l['movie_id'] == data['movie_id']), None)
  if existing:
    return jsonify({'error': 'Link with this movie_id already exists'}), 400
  
  new_link = {
    'movie_id': data['movie_id'],
    'imdb_id': data.get('imdb_id', ''),
    'tmdb_id': data.get('tmdb_id', '')
  }
  links_data.append(new_link)
  return jsonify(new_link), 201

@app.route('/links/<movie_id>', methods=['PUT'])
def update_link(movie_id):
  global links_data
  if not links_data:
    get_links()
  
  link = next((l for l in links_data if l['movie_id'] == movie_id), None)
  if link is None:
    return jsonify({'error': 'Link not found'}), 404
  
  data = request.get_json()
  if 'imdb_id' in data:
    link['imdb_id'] = data['imdb_id']
  if 'tmdb_id' in data:
    link['tmdb_id'] = data['tmdb_id']
  
  return jsonify(link)

@app.route('/links/<movie_id>', methods=['DELETE'])
def delete_link(movie_id):
  global links_data
  if not links_data:
    get_links()
  
  link = next((l for l in links_data if l['movie_id'] == movie_id), None)
  if link is None:
    return jsonify({'error': 'Link not found'}), 404
  
  links_data.remove(link)
  return jsonify({'message': 'Link deleted successfully'}), 200



@app.route('/ratings')
def get_ratings():
  global ratings_data
  if not ratings_data:
    csv_path = get_csv_path('ratings.csv')
    ratings = []
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
    for encoding in encodings:
      try:
        with open(csv_path, newline='', encoding=encoding) as csvfile:
          reader = csv.DictReader(csvfile)
          for row in reader:
            user_id = row['userId']
            movie_id = row['movieId']
            rating = row['rating']
            timestamp = row['timestamp']
            rating_obj = Rating(user_id, movie_id, rating, timestamp)
            ratings.append(rating_obj.__dict__)
        ratings_data = ratings
        break
      except (UnicodeDecodeError, KeyError) as e:
        ratings = []
        continue
  return jsonify(ratings_data)

@app.route('/ratings/<int:rating_id>', methods=['GET'])
def get_rating(rating_id):
  global ratings_data
  if not ratings_data:
    get_ratings()
  
  if rating_id >= len(ratings_data):
    return jsonify({'error': 'Rating not found'}), 404
  return jsonify(ratings_data[rating_id])

@app.route('/ratings', methods=['POST'])
def create_rating():
  global ratings_data
  if not ratings_data:
    get_ratings()
  
  data = request.get_json()
  if not data or 'user_id' not in data or 'movie_id' not in data or 'rating' not in data:
    return jsonify({'error': 'Missing required fields: user_id, movie_id, rating'}), 400
  
  new_rating = {
    'user_id': data['user_id'],
    'movie_id': data['movie_id'],
    'rating': data['rating'],
    'timestamp': data.get('timestamp', '0')
  }
  ratings_data.append(new_rating)
  return jsonify(new_rating), 201

@app.route('/ratings/<int:rating_id>', methods=['PUT'])
def update_rating(rating_id):
  global ratings_data
  if not ratings_data:
    get_ratings()
  
  if rating_id >= len(ratings_data):
    return jsonify({'error': 'Rating not found'}), 404
  
  data = request.get_json()
  if 'user_id' in data:
    ratings_data[rating_id]['user_id'] = data['user_id']
  if 'movie_id' in data:
    ratings_data[rating_id]['movie_id'] = data['movie_id']
  if 'rating' in data:
    ratings_data[rating_id]['rating'] = data['rating']
  if 'timestamp' in data:
    ratings_data[rating_id]['timestamp'] = data['timestamp']
  
  return jsonify(ratings_data[rating_id])

@app.route('/ratings/<int:rating_id>', methods=['DELETE'])
def delete_rating(rating_id):
  global ratings_data
  if not ratings_data:
    get_ratings()
  
  if rating_id >= len(ratings_data):
    return jsonify({'error': 'Rating not found'}), 404
  
  deleted = ratings_data.pop(rating_id)
  return jsonify({'message': 'Rating deleted successfully'}), 200


@app.route('/tags')
def get_tags():
  global tags_data
  if not tags_data:
    csv_path = get_csv_path('tags.csv')
    tags = []
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
    for encoding in encodings:
      try:
        with open(csv_path, newline='', encoding=encoding) as csvfile:
          reader = csv.DictReader(csvfile)
          for row in reader:
            user_id = row['userId']
            movie_id = row['movieId']
            tag = row['tag']
            timestamp = row['timestamp']
            tag_obj = Tag(user_id, movie_id, tag, timestamp)
            tags.append(tag_obj.__dict__)
        tags_data = tags
        break
      except (UnicodeDecodeError, KeyError) as e:
        tags = []
        continue
  return jsonify(tags_data)

@app.route('/tags/<int:tag_id>', methods=['GET'])
def get_tag(tag_id):
  global tags_data
  if not tags_data:
    get_tags()
  
  if tag_id >= len(tags_data):
    return jsonify({'error': 'Tag not found'}), 404
  return jsonify(tags_data[tag_id])

@app.route('/tags', methods=['POST'])
def create_tag():
  global tags_data
  if not tags_data:
    get_tags()
  
  data = request.get_json()
  if not data or 'user_id' not in data or 'movie_id' not in data or 'tag' not in data:
    return jsonify({'error': 'Missing required fields: user_id, movie_id, tag'}), 400
  
  new_tag = {
    'user_id': data['user_id'],
    'movie_id': data['movie_id'],
    'tag': data['tag'],
    'timestamp': data.get('timestamp', '0')
  }
  tags_data.append(new_tag)
  return jsonify(new_tag), 201

@app.route('/tags/<int:tag_id>', methods=['PUT'])
def update_tag(tag_id):
  global tags_data
  if not tags_data:
    get_tags()
  
  if tag_id >= len(tags_data):
    return jsonify({'error': 'Tag not found'}), 404
  
  data = request.get_json()
  if 'user_id' in data:
    tags_data[tag_id]['user_id'] = data['user_id']
  if 'movie_id' in data:
    tags_data[tag_id]['movie_id'] = data['movie_id']
  if 'tag' in data:
    tags_data[tag_id]['tag'] = data['tag']
  if 'timestamp' in data:
    tags_data[tag_id]['timestamp'] = data['timestamp']
  
  return jsonify(tags_data[tag_id])

@app.route('/tags/<int:tag_id>', methods=['DELETE'])
def delete_tag(tag_id):
  global tags_data
  if not tags_data:
    get_tags()
  
  if tag_id >= len(tags_data):
    return jsonify({'error': 'Tag not found'}), 404
  
  deleted = tags_data.pop(tag_id)
  return jsonify({'message': 'Tag deleted successfully'}), 200

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/movies')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True)