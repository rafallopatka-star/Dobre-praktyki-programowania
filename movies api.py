from flask import Flask, jsonify
import csv
import os
import webbrowser
import threading

app = Flask(__name__)

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
      break
    except (UnicodeDecodeError, KeyError) as e:
      if isinstance(e, KeyError):
        print(f"Błąd klucza: {e}, Dostępne klucze: {list(row.keys()) if 'row' in locals() else 'brak'}")
      movies = []
      continue
  return jsonify(movies)

@app.route('/links')
def get_links():
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
      break
    except (UnicodeDecodeError, KeyError) as e:
      links = []
      continue
  return jsonify(links)

@app.route('/ratings')
def get_ratings():
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
      break
    except (UnicodeDecodeError, KeyError) as e:
      ratings = []
      continue
  return jsonify(ratings)

@app.route('/tags')
def get_tags():
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
      break
    except (UnicodeDecodeError, KeyError) as e:
      tags = []
      continue
  return jsonify(tags)

def open_browser():
    webbrowser.open_new('http://127.0.0.1:5000/movies')

if __name__ == '__main__':
    threading.Timer(1.5, open_browser).start()
    app.run(debug=True)