import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries

create_query="""
-- Create dimension table: users
CREATE TABLE users (
    user_id INT PRIMARY KEY,
    first_name VARCHAR(128) NOT NULL,
    last_name VARCHAR(128) NOT NULL,
    gender CHAR(1) NOT NULL,
    level VARCHAR(10) NOT NULL
);


-- Create dimension table: artists
CREATE TABLE artists (
    artist_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(256) NOT NULL,
    location VARCHAR(256),
    latitude DECIMAL(9,6),
    longitude DECIMAL(9,6)
);


-- Create dimension table: songs
CREATE TABLE songs (
    song_id VARCHAR(20) PRIMARY KEY,
    title VARCHAR(256) NOT NULL,
    artist_id VARCHAR(20) NOT NULL REFERENCES artists(artist_id),
    year INT NOT NULL,
    duration DECIMAL(10,5) NOT NULL
);


-- Create dimension table: time
CREATE TABLE time (
    start_time TIMESTAMP PRIMARY KEY,
    hour INT NOT NULL,
    day INT NOT NULL,
    week INT NOT NULL,
    month INT NOT NULL,
    year INT NOT NULL,
    weekday INT NOT NULL
);

-- Create fact table: songplays
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
"""

drop_query="""
DROP TABLE IF EXISTS songplays, time, songs, artists, users;
"""

show_query="""
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
"""

from pprint import pprint
    
def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')

    vals = list(config['CLUSTER'].values())
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*vals))
    cur = conn.cursor()
    
    def _query(q: str):
        print(f"Executing the following query: \n{q}")
        cur.execute(q.strip())
        try:
            rows = cur.fetchall()
            pprint(rows)            
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e):
                pass
            else:
                raise e
        conn.commit()
    
    _query(drop_query)
    _query(create_query)
    _query(show_query)

    conn.close()


if __name__ == "__main__":
    main()