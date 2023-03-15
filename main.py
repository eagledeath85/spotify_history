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
    DB_NAME = "test_my_spotify_history.db"

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

    Attributes:
    ----------
    table_to_insert: tuple
        The table to create into the database

    Methods:
    -------
    create_table():
        create a given table in the dB
        insert_into_table():
            alter the table by adding data
        read_db():
            TBD
    """

    def __init__(self, table_to_insert: dict = None, song_to_insert=None):
        # self.song_to_insert = None
        self.song_to_insert = song_to_insert
        self.table_to_insert = table_to_insert
        # self.artist_table, self.song_table = table_to_insert.values()

        # self.table_name = table_to_insert[0]
        # self.columns_to_insert = table_to_insert[1]
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

    def insert_into_artist_table(self, song_to_insert):
        artist_name = song_to_insert.get_artist()
        cursor = Database.create_cursor()
        if artist_name not in self.artist_id_artist_name_dict.values():
            cursor.execute(f"INSERT INTO artist (artist_name) "
                           f"VALUES (\'{artist_name}')")
            self.artist_last_row_id = cursor.lastrowid
            self.artist_id_artist_name_dict.update(
                {self.artist_last_row_id: artist_name})

            """
            # Insert into song table
            case 'song':

                insert_to_album_table_sql_request = f"INSERT INTO {self.table_name} ({self.artist_last_row_id}," \
                                                    f" {Song.get_track(self.song_to_insert)}, " \
                                                    f"{Song.get_date_of_playing(self.song_to_insert)}) " \
                                                    f"VALUES ({song} ({self.artist_last_row_id}, " \
                                                    f"{Song.get_track(self.song_to_insert)}, " \
                                                    f"{Song.get_date_of_playing(self.song_to_insert)})"
                cursor.execute(insert_to_album_table_sql_request)
            """

    def read_db(self):
        pass


# MAIN PROGRAM

# 1. Open, Read and save the json data into a dictionary
try:
    with open(filename, 'r', encoding='utf-8', newline='') as json_file_to_read:
        data_from_json_file = json_file_to_read.read()
        data = json.loads(data_from_json_file)
except FileNotFoundError:
    print("ERROR: The file doesn't exist, please check your file path")

# 2. Building the database
# 2.1 Create a database object and create artist table
database = DatabaseActions()  # previous version: DatabaseActions(table_artist)
database.create_table()
# 2.2 Insert data into the artist table
for song_data_dict in data:
    song = Song(song_data_dict)
    database.insert_into_artist_table(song)
Database.commit_changes()
Database.close_connection()
# 2.3 Create a database object and create song table
database = DatabaseActions(table_song)
database.create_table()
# 2.4 Insert data into the song table
for song_data_dict in data:
    song = Song(song_data_dict)
    database.insert_into_artist_table(song)
Database.commit_changes()
Database.close_connection()
