from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()

class Movie(Base):
    __tablename__ = 'movies'
    
    movie_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    genres = Column(String)

class Link(Base):
    __tablename__ = 'links'
    
    movie_id = Column(Integer, primary_key=True)
    imdb_id = Column(String)
    tmdb_id = Column(String)

class Rating(Base):
    __tablename__ = 'ratings'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    movie_id = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    timestamp = Column(Integer)

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    movie_id = Column(Integer, nullable=False)
    tag = Column(String, nullable=False)
    timestamp = Column(Integer)

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE_URL = f"sqlite:///{os.path.join(DB_DIR, 'movies.db')}"

def get_engine():
    return create_engine(DATABASE_URL, echo=False)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def create_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
