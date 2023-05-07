import configparser
import psycopg2
from sql_queries import create_table_queries, drop_table_queries

create_query="""
-- Create fact table: songplays
CREATE TABLE songplays (
  songplay_id SERIAL PRIMARY KEY,
  start_time BIGINT NOT NULL,
  user_id INT NOT NULL,
  level VARCHAR(10),
  song_id VARCHAR(50),
  artist_id VARCHAR(50),
  session_id INT,
  location VARCHAR(255),
  user_agent VARCHAR(255)
);

-- Create dimension table: users
CREATE TABLE users (
  user_id INT PRIMARY KEY,
  first_name VARCHAR(50),
  last_name VARCHAR(50),
  gender CHAR(1),
  level VARCHAR(10)
);

-- Create dimension table: songs
CREATE TABLE songs (
  song_id VARCHAR(50) PRIMARY KEY,
  title VARCHAR(255),
  artist_id VARCHAR(50),
  year INT,
  duration DECIMAL(10, 5)
);

-- Create dimension table: artists
CREATE TABLE artists (
  artist_id VARCHAR(50) PRIMARY KEY,
  name VARCHAR(255),
  location VARCHAR(255),
  latitude DECIMAL(9, 6),
  longitude DECIMAL(9, 6)
);

-- Create dimension table: time
CREATE TABLE time (
  start_time BIGINT PRIMARY KEY,
  hour INT,
  day INT,
  week INT,
  month INT,
  year INT,
  weekday INT
);
"""

def drop_tables(cur, conn):
    return
    for query in drop_table_queries:
        cur.execute(query)
        conn.commit()


def create_tables(cur, conn):
    # for query in create_table_queries:
    cur.execute(create_query.strip())
    conn.commit()

    
import os
import dotenv
dotenv.load_dotenv()

def main():
    config = configparser.ConfigParser()
    config.read('dwh.cfg')
    print(config)

    vals = list(config['CLUSTER'].values())
    print(vals)
    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*vals))
    cur = conn.cursor()

    drop_tables(cur, conn)
    create_tables(cur, conn)

    conn.close()


if __name__ == "__main__":
    main()