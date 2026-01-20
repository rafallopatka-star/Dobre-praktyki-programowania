import csv
import os
from SQL.database_models import Movie, Link, Rating, Tag, create_tables, get_session

def get_csv_path(filename):
    downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads', 'database', filename)
    if os.path.exists(downloads_path):
        return downloads_path
    return filename

def load_movies():
    csv_path = get_csv_path('movies.csv')
    session = get_session()
    
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
                        print(f"Załadowano {count} filmów...")
                session.commit()
                print(f"Załadowano {count} filmów")
            break
        except Exception as e:
            print(f"Błąd: {e}")
            continue
    
    session.close()

def load_links():
    csv_path = get_csv_path('links.csv')
    session = get_session()
    
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
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
                        print(f"Załadowano {count} linków...")
                session.commit()
                print(f"Załadowano {count} linków")
            break
        except Exception as e:
            print(f"Błąd: {e}")
            continue
    
    session.close()

def load_ratings():
    csv_path = get_csv_path('ratings.csv')
    session = get_session()
    
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
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
                        print(f"Załadowano {count} ocen...")
                session.commit()
                print(f"✓ Załadowano {count} ocen")
            break
        except Exception as e:
            print(f"Błąd: {e}")
            continue
    
    session.close()

def load_tags():
    csv_path = get_csv_path('tags.csv')
    session = get_session()
    
    encodings = ['utf-8', 'latin-1', 'windows-1252', 'iso-8859-1']
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
                        print(f"Załadowano {count} tagów...")
                session.commit()
                print(f"✓ Załadowano {count} tagów")
            break
        except Exception as e:
            print(f"Błąd: {e}")
            continue
    
    session.close()

if __name__ == '__main__':
    print("Tworzenie tabel...")
    create_tables()
    print("✓ Tabele utworzone\n")
    
    print("Ładowanie danych z plików CSV...")
    load_movies()
    load_links()
    load_ratings()
    load_tags()
    
    print("\n✓ Wszystkie dane zostały załadowane do bazy!")

