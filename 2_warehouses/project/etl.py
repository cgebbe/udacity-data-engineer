import utils

config = utils.read_config()
role = config["IAM_ROLE"]["ARN"]

song_queries = dict()
song_queries["drop"] = utils.get_drop_query("song_stage_table")
song_queries[
    "create"
] = """

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
"""

event_queries = dict()
event_queries["drop"] = utils.get_drop_query("event_stage_table")
event_queries[
    "create"
] = """
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
"""
event_queries[
    "copy"
] = f"""
COPY event_stage_table
FROM 's3://udacity-dend/log-data'
IAM_ROLE {role}
--JSON 'auto' -- doesn't work, because keys don't match perfectly
JSON 's3://udacity-dend/log_json_path.json'
STATUPDATE ON
MAXERROR 1
COMPUPDATE OFF;
"""
event_queries["list"] = utils.get_list_query("event_stage_table")
event_queries["count"] = utils.get_count_query("event_stage_table")


song_queries[
    "stage_songs"
] = f"""
COPY song_stage_table
FROM 's3://udacity-dend/song_data/A/A/A/'
IAM_ROLE {role}
JSON 'auto'
STATUPDATE ON
MAXERROR 1
COMPUPDATE OFF;
"""


song_queries["list"] = utils.get_list_query("song_stage_table")
song_queries["count"] = utils.get_count_query("song_stage_table")

load_queries = dict()
load_queries[
    "load"
] = """
-- load artists
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
FROM song_stage_table;

-- load songs
INSERT INTO songs (song_id, title, artist_id, year, duration)
SELECT DISTINCT song_id, title, artist_id, year, duration
FROM song_stage_table;

-- load users
INSERT INTO users (user_id, first_name, last_name, gender, level)
SELECT DISTINCT userId, firstName, lastName, gender, level
FROM event_stage_table
WHERE userId IS NOT NULL;

-- load time
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

-- load songplays
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
"""

# load_queries = dict()
for t in ["songplays", "time", "songs", "artists", "users"]:
    load_queries[f"list_{t}"] = utils.get_list_query(t)
    load_queries[f"count_{t}"] = utils.get_count_query(t)

query = """
SELECT *
FROM event_stage_table
WHERE ts = '1541105830796'
LIMIT 3
"""


def main():
    with utils.Connection() as conn:
        if 0:
            conn.run(query)
        else:
            for k, v in load_queries.items():
                print(f"### {k.upper()}")
                conn.run(v)


if __name__ == "__main__":
    main()
