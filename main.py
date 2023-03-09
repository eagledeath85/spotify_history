import json
import os
import re
import sqlite3
from timeit import default_timer as timer
from tables import table_artist, table_song

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
        cursor = Database.connect_to_db().cursor()
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

    def __init__(self, table_to_insert: tuple):
        self.song_to_insert = None
        self.table_to_insert = table_to_insert

        self.table_name = table_to_insert[0]
        self.columns_to_insert = table_to_insert[1]
        self.artist_last_row_id = 0
        self.artist_id_artist_name_dict = {}

    def create_table(self):
        # Getting table_name and columns name to add to the table
        table_name = self.table_name
        columns_to_insert = self.columns_to_insert
        columns_list = []
        for column_name in columns_to_insert:
            columns_list.append(column_name)

        # Create a cursor object and create table
        cursor = Database.create_cursor()
        create_table_sql_request = f"CREATE TABLE {table_name} ({columns_list.pop(0)} INTEGER NOT NULL PRIMARY KEY)"
        cursor.execute(create_table_sql_request)
        for column in columns_list:
            alter_table_sql_request = f"ALTER TABLE {table_name} ADD {column} VARCHAR"
            cursor.execute(alter_table_sql_request)

        # Commit the changes and close the connection
        Database.commit_changes()
        Database.close_connection()

    def insert_into_table(self, song_to_insert=None):
        self.song_to_insert = song_to_insert
        cursor = Database.create_cursor()

        # Insert into artist table
        match self.table_name:
            case 'artist':
                # Check if artist_name already exists in the artist table
                if not Song.get_artist(self.song_to_insert) in self.artist_id_artist_name_dict.values():
                    # self.columns_to_insert[1] = artist_name
                    cursor.execute(f"INSERT INTO {self.table_name} ({self.columns_to_insert[1]}) "
                                   f"VALUES (\'{Song.get_artist(self.song_to_insert)}')")
                    self.artist_last_row_id = cursor.lastrowid
                    self.artist_id_artist_name_dict.update(
                        {self.artist_last_row_id: Song.get_artist(self.song_to_insert)})

            case 'song':
                # Insert into song table
                insert_to_album_table_sql_request = f"INSERT INTO {self.table_name} ({self.artist_last_row_id}," \
                                                    f" {Song.get_track(self.song_to_insert)}, " \
                                                    f"{Song.get_date_of_playing(self.song_to_insert)}) " \
                                                    f"VALUES ({song} ({self.artist_last_row_id}, " \
                                                    f"{Song.get_track(self.song_to_insert)}, " \
                                                    f"{Song.get_date_of_playing(self.song_to_insert)})"
                cursor.execute(insert_to_album_table_sql_request)

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

# 2. Create a database object and create table_artist table
database = DatabaseActions(table_artist)
database.create_table()

# 3. Insert
# start = timer()
for song_data_dict in data:
    song = Song(song_data_dict)
    database.insert_into_table(song)
Database.commit_changes()
Database.close_connection()
# end = timer()
# print(end - start)
# database = Database(table_song, song)
# database.create_table()
# database.insert_into_table()
