import json
import os
import re
import sqlite3
import datetime
from timeit import default_timer as timer

# class Database
# table
# name
# column 1
# column 2
# ...

# createTable
# writeDataToTable
# deleteDataFromTable
# commitChanges


# 1. Build file path
PATH = "/home/administrateur/Downloads/my_spotify_data/MyData/"
file = "StreamingHistory0.json"  # TODO: find files automatically and choose one randomly
filename = os.path.join(PATH, file)


class Song:
    """
    Create a song object

    Attributes:
    -----------
    song_data: dict
        The song information

    Methods:
    --------
    get_artist():
        return the artistName
    get_track():
        return the trackName
    get_duration():
        return the track duration
    get_date_of_playing():
        return the date when the song wa played
    """

    def __init__(self, song_data: dict):
        self.song_data = song_data

    def get_artist(self):
        # artistName can have special characters such as "'".
        # We need to address them to insert the artistName in the artist table
        if not self.song_data['artistName'].isalnum():
            self.song_data['artistName'] = re.sub("'", " ", self.song_data['artistName'])
        return self.song_data['artistName']

    def get_track(self):
        if not self.song_data['trackName'].isalnum():
            self.song_data['trackName'] = re.sub("'", " ", self.song_data['trackName'])
        return self.song_data['trackName']

    def get_duration(self):
        # Convert the duration in MM:SS format
        self.song_data['msPlayed'] = datetime.datetime.fromtimestamp(self.song_data['msPlayed'] / 1000.0).strftime(
            "%M:%S")
        return self.song_data['msPlayed']

    def get_date_of_playing(self):
        return self.song_data['endTime']


class Database:
    """
    Create an instance to connect to a database

    Attributes:
    ----------
    db_name: str
        The database name to create and connect to

    Methods:
    -------
    connect_to_db():
        returns a connection object
    create_cursor():
        returns a cursor object
    commit_changes():
        ensures the changes made in the database are consistent
    close_connection():
        safely close the connection to the database
    """
    DB_NAME = "my_spotify_history.db"

    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name

    @staticmethod
    def connect_to_db():
        try:
            connection = sqlite3.connect(Database.DB_NAME, isolation_level=None)
        except sqlite3.Error as er:
            print('SQLite error: %s' % (' '.join(er.args)))
        else:
            return connection

    @staticmethod
    def create_cursor():
        try:
            cursor = Database.connect_to_db().cursor()
        except sqlite3.Error as error:
            print("Error while creating cursor object", error)
        return cursor

    @staticmethod
    def commit_changes():
        Database.connect_to_db().commit()

    @staticmethod
    def close_connection():
        Database.connect_to_db().close()


class DatabaseActions:
    """
    Create a database instance to write data into

    Methods:
    -------
    create_table():
        create a given table in the dB
    insert_into_artist_table():
        alter the artist table by adding data
    insert_into_song_table():
        alter the artist table by adding data
    """

    def __init__(self):
        self.artist_last_row_id = 0
        self.artist_id_artist_name_dict = {}

    @staticmethod
    def create_table():
        cursor = Database.create_cursor()
        # Reading the sql script and executing the sql requests
        with open('tables_to_create.sql', 'r', encoding='utf-8', newline='') as sqlite_file:
            sql_script = sqlite_file.read()
        cursor.executescript(sql_script)
        print("SQLite script executed successfully")

        # Commit the changes and close the connection
        Database.commit_changes()
        Database.close_connection()

    def insert_into_artist_table(self, song_to_insert: Song):
        artist_name = song_to_insert.get_artist()
        cursor = Database.create_cursor()
        if artist_name not in self.artist_id_artist_name_dict.values():
            cursor.execute(f"INSERT INTO artist (artist_name) "
                           f"VALUES (\'{artist_name}')")
            self.artist_last_row_id = cursor.lastrowid
            # Create a dictionary {self.artist_last_row_id:  artist_name}
            self.artist_id_artist_name_dict.update(
                {self.artist_last_row_id: artist_name})

    def insert_into_song_table(self, song_to_insert: Song):
        artist_name = song_to_insert.get_artist()
        song_name = song_to_insert.get_track()
        song_duration = song_to_insert.get_duration()
        song_playing_date = song_to_insert.get_date_of_playing()
        song_artist_id_key = [i for i in self.artist_id_artist_name_dict if
                              self.artist_id_artist_name_dict[i] == artist_name]
        song_artist_id = int(song_artist_id_key[0])
        cursor = Database.create_cursor()
        cursor.execute(
            f"INSERT INTO song (artist_id, song_name, duration, playing_date) "
            f"VALUES ({song_artist_id}, \'{song_name}', \'{song_duration}', \'{song_playing_date}')")


# MAIN PROGRAM
print("PROGRAM STARTS")
# 1. Open, Read and save the json data into a dictionary
try:
    with open(filename, 'r', encoding='utf-8', newline='') as json_file_to_read:
        data_from_json_file = json_file_to_read.read()
        data = json.loads(data_from_json_file)
except FileNotFoundError:
    print("ERROR: The file doesn't exist, please check your file path")

# 2. Building the database
# 2.1 Create a database object and create artist, song tables
database = DatabaseActions()
database.create_table()

# 2.2 Insert data into artist table and song_table
for song_data_dict in data:
    song = Song(song_data_dict)
    database.insert_into_artist_table(song)
    database.insert_into_song_table(song)

# 2.3 Commit changes and close connection to dB
Database.commit_changes()
Database.close_connection()
print("END OF PROGRAM")
