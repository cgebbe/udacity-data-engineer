import configparser
import utils

# CONFIG
config = configparser.ConfigParser()
config.read("dwh.cfg")
role = config["IAM_ROLE"]["ARN"]

# DROP TABLES
staging_events_table_drop = utils.get_drop_query("event_stage_table")
staging_songs_table_drop = utils.get_drop_query("song_stage_table")
songplay_table_drop = utils.get_drop_query("songplays")
user_table_drop = utils.get_drop_query("users")
song_table_drop = utils.get_drop_query("songs")
artist_table_drop = utils.get_drop_query("artists")
time_table_drop = utils.get_drop_query("time")

# CREATE TABLES

staging_events_table_create = """
CREATE TABLE event_stage_table (
    artist VARCHAR(255),
    auth VARCHAR(255),
    firstName VARCHAR(255),
    gender CHAR(1),
    itemInSession SMALLINT,
    lastName VARCHAR(255),
    length FLOAT,
    level VARCHAR(50),
    location VARCHAR(255),
    method VARCHAR(10),
    page VARCHAR(50),
    registration BIGINT,
    sessionId INTEGER,
    song VARCHAR(255),
    status SMALLINT,
    ts BIGINT,
    userAgent VARCHAR(255),
    userId INTEGER
);
""".strip()

staging_songs_table_create = """
CREATE TABLE song_stage_table (
    artist_id VARCHAR(50),
    artist_latitude FLOAT,
    artist_location VARCHAR(500),
    artist_longitude FLOAT,
    artist_name VARCHAR(500),
    duration FLOAT,
    num_songs INT,
    song_id VARCHAR(50),
    title VARCHAR(500),
    year INT
);
""".strip()

songplay_table_create = """
CREATE TABLE songplays (
    songplay_id INT IDENTITY(0,1) PRIMARY KEY,
    start_time TIMESTAMP NOT NULL,
    user_id INT NOT NULL REFERENCES users(user_id),
    level VARCHAR(10) NOT NULL,
    song_id VARCHAR(20) NOT NULL REFERENCES songs(song_id),
    artist_id VARCHAR(20) NOT NULL REFERENCES artists(artist_id),
    session_id INT NOT NULL,
    location VARCHAR(256),
    user_agent VARCHAR(512)
);
""".strip()

user_table_create = """
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    gender CHAR(1) NOT NULL,
    level VARCHAR(10) NOT NULL
);
""".strip()

song_table_create = """
CREATE TABLE songs (
    song_id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    artist_id VARCHAR(20) NOT NULL REFERENCES artists(artist_id),
    year INT NOT NULL,
    duration DECIMAL(10,5) NOT NULL
);
""".strip()

artist_table_create = """
CREATE TABLE artists (
    artist_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    location VARCHAR(256),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);
""".strip()

time_table_create = """
CREATE TABLE time (
    start_time TIMESTAMP PRIMARY KEY,
    hour INT NOT NULL,
    day INT NOT NULL,
    week INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    weekday INT NOT NULL
);
""".strip()

# STAGING TABLES

staging_events_copy = f"""
COPY event_stage_table
FROM 's3://udacity-dend/log-data'
IAM_ROLE {role}
--JSON 'auto' -- doesn't work, because keys don't match perfectly
JSON 's3://udacity-dend/log_json_path.json'
STATUPDATE ON
MAXERROR 1
COMPUPDATE OFF;
""".strip()

staging_songs_copy = f"""
COPY song_stage_table
-- FROM 's3://udacity-dend/song_data/A/A/A/' -- use subset
FROM 's3://udacity-dend/song_data/'
IAM_ROLE {role}
JSON 'auto'
STATUPDATE ON
MAXERROR 1
COMPUPDATE OFF;
""".strip()

# FINAL TABLES

songplay_table_insert = """
INSERT INTO songplays (start_time, user_id, level, song_id, artist_id, session_id, location, user_agent)
SELECT
    TIMESTAMP 'epoch' + e.ts/1000 * INTERVAL '1 second' AS start_time,
    e.userId,
    e.level,
    s.song_id,
    s.artist_id,
    e.sessionId,
    e.location,
    e.userAgent
FROM event_stage_table e
JOIN songs s ON e.song = s.title
JOIN artists a ON e.artist = a.name AND s.artist_id = a.artist_id
WHERE e.page = 'NextSong';
""".strip()

user_table_insert = """
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT userId, firstName, lastName, gender, level
FROM event_stage_table
WHERE userId IS NOT NULL;
""".strip()

song_table_insert = """
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT song_id, title, artist_id, year, duration
FROM song_stage_table;
""".strip()

artist_table_insert = """
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
FROM song_stage_table;
""".strip()

time_table_insert = """
INSERT INTO time (start_time, hour, day, week, month, year, weekday)
SELECT DISTINCT
    TIMESTAMP 'epoch' + ts/1000 * INTERVAL '1 second' AS start_time,
    EXTRACT(hour FROM start_time) AS hour,
    EXTRACT(day FROM start_time) AS day,
    EXTRACT(week FROM start_time) AS week,
    EXTRACT(month FROM start_time) AS month,
    EXTRACT(year FROM start_time) AS year,
    EXTRACT(weekday FROM start_time) AS weekday
FROM event_stage_table
WHERE ts IS NOT NULL;
""".strip()

# QUERY LISTS

create_table_queries = [
    staging_events_table_create,
    staging_songs_table_create,
    user_table_create,
    artist_table_create,
    time_table_create,
    song_table_create,
    songplay_table_create,
]
drop_table_queries = [
    staging_events_table_drop,
    staging_songs_table_drop,
    songplay_table_drop,
    song_table_drop,
    user_table_drop,
    artist_table_drop,
    time_table_drop,
]
copy_table_queries = [
    staging_events_copy,
    staging_songs_copy,
]
insert_table_queries = [
    user_table_insert,
    artist_table_insert,
    time_table_insert,
    song_table_insert,
    songplay_table_insert,
]
