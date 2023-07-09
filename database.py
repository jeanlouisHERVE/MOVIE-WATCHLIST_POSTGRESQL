#title, release_date, watched
import os
import datetime
import psycopg2

from dotenv import load_dotenv

load_dotenv()

CREATE_MOVIES_TABLE = """CREATE TABLE IF NOT EXISTS movies (
    id INTEGER PRIMARY KEY,
    title TEXT,
    release_timestamp REAL
);"""

CREATE_USERNAME_TABLE = """CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY
);"""

CREATE_WATCHED_TABLE = """CREATE TABLE IF NOT EXISTS watched (
    user_username TEXT,
    movie_id INTEGER,
    FOREIGN KEY(user_username) REFERENCES users(username),
    FOREIGN KEY(movie_id) REFERENCES movies(id)
);"""

INSERT_MOVIES = "INSERT INTO movies (title, release_timestamp) VALUES (?, ?);"
INSERT_USER = "INSERT INTO users (username) VALUES (?);"
INSERT_WATCHED_MOVIES = "INSERT INTO watched (user_username, movie_id) VALUES (?, ?);"
SELECT_ALL_MOVIES = "SELECT * FROM movies;"
SELECT_UPCOMING_MOVIES = "SELECT * FROM movies WHERE release_timestamp > ?;"
SELECT_WATCHED_MOVIES = """SELECT movies.* FROM movies
JOIN watched ON movies.id = watched.movie_id
JOIN users ON users.username = watched.user_username
WHERE users.username= ?;"""
SET_MOVIE_WATCHED = "UPDATE movies SET watched = 1 WHERE title = ?;"
SEARCH_MOVIES = "SELECT * FROM movies WHERE title LIKE ?;"
DELETE_MOVIE = "DELETE FROM movies WHERE title = ?;"
CREATE_RELEASE_INDEX = "CREATE INDEX IF NOT EXISTS idx_movies_release ON movies(release_timestamp);"

connection = psycopg2.connect(os.environ["DATABASE_URL"])

def create_table():
    with connection:
        #the order of creation is important !
        connection.execute(CREATE_MOVIES_TABLE)
        connection.execute(CREATE_USERNAME_TABLE)
        connection.execute(CREATE_WATCHED_TABLE)
        connection.execute(CREATE_RELEASE_INDEX)
        
def add_user(username):
    with connection:
        connection.execute(INSERT_USER, (username,))

def add_movie(title, release_timestamp):
    with connection:
        connection.execute(INSERT_MOVIES, (title, release_timestamp))

def get_movies(upcoming=False):
    with connection:
        cursor = connection.cursor()
        if upcoming:
            today_timestamp = datetime.datetime.today().timestamp()
            cursor.execute(SELECT_UPCOMING_MOVIES, (today_timestamp,))
        else:
            cursor.execute(SELECT_ALL_MOVIES)
        return cursor.fetchall()

def search_movies(search_term):
    with connection:
        cursor = connection.cursor()
        connection.execute(SEARCH_MOVIES, (f"%{search_term}%", ))
        return cursor.fetchall()

def watch_movie(username, movie_id):
    with connection:
        connection.execute(INSERT_WATCHED_MOVIES, (username, movie_id))
        
def get_watched_movies(username):
    with connection:
        cursor = connection.cursor()
        cursor.execute(SELECT_WATCHED_MOVIES, (username, ))
        return cursor.fetchall()