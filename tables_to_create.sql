CREATE TABLE artist (
artist_id INTEGER NOT NULL PRIMARY KEY,
artist_name VARCHAR
);

CREATE TABLE song (
song_id INTEGER NOT NULL PRIMARY KEY,
artist_id INTEGER,
song_name VARCHAR,
duration TIME,
playing_date timestamp
);

