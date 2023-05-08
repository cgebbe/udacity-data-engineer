# Project: Data Warehouse

- [Project: Data Warehouse](#project-data-warehouse)
  - [Discuss the purpose of this database in context of the startup, Sparkify, and their analytical goals](#discuss-the-purpose-of-this-database-in-context-of-the-startup-sparkify-and-their-analytical-goals)
  - [State and justify your database schema design and ETL pipeline](#state-and-justify-your-database-schema-design-and-etl-pipeline)
    - [database table schema](#database-table-schema)
    - [staging table schema](#staging-table-schema)
    - [Extract and transform step](#extract-and-transform-step)
    - [Load step](#load-step)
  - [Provide example queries and results for song play analysis](#provide-example-queries-and-results-for-song-play-analysis)
    - [Top 10 songs](#top-10-songs)
    - [Number of active users per week](#number-of-active-users-per-week)
    - [Gender distribution of users](#gender-distribution-of-users)


## Discuss the purpose of this database in context of the startup, Sparkify, and their analytical goals

The purpose of this database is to provide Sparkify with a structured and organized way to store, access, and analyze their data related to user activity and song metadata. By leveraging a cloud-based solution such as Amazon Redshift, Sparkify can scale their data storage and processing capabilities as their user base and song catalog grow.

The star schema, consisting of a fact table (songplays) and multiple dimension tables (users, songs, artists, and time), is designed to optimize query performance for analytical purposes and is also easily understandable. This schema allows Sparkify's analytics team to efficiently extract insights about user behavior, preferences, and trends that can help inform business decisions and drive growth.

Some analytical goals for Sparkify may include:

- Understanding user preferences and listening habits to inform marketing and promotional efforts.
- Identifying popular songs, artists, and genres to better curate their music catalog and enhance user experience.
- Analyzing user demographics and regional trends to optimize targeted advertising and expand into new markets.


## State and justify your database schema design and ETL pipeline

### database table schema

Explanation of chosen data types:

- VARCHAR: Variable-length character data type is used for text-based data like names, locations, user_agent, etc. The length parameter is provided based on an estimation of the maximum expected length of the data.
- INT: Integer data type is used for whole numbers like user_id, session_id, year, and various time-related fields.
- TIMESTAMP: Timestamp data type is used for start_time to store the date and time of the event.
- FLOAT: FLOAT type is used for numeric values such as duration, latitude, and longitude. Alternatively, we could have used DECIMAL.
- CHAR: Fixed-length character data type is used for gender since it only has one character (M or F).

Other keywords

- REFERENCES: This keyword is used to define a foreign key constraint between columns of different tables. It ensures that any value inserted into e.g. the `user_id` column of the `songplays` table must already exist in the `user_id` column of the `users` table, preventing orphaned rows. Note that when using this keywords, tables need to be created in a certain order.
- IDENTITY(0,1): This keyword is used to create an auto-incrementing column in a table. It starts at zero and increments by one.


### staging table schema

There's really nothing new in the definition of the two staging tables.

### Extract and transform step

We use two `COPY` statements to copy the JSON files from S3 into the staging tables. The songs can be staged by specifying `JSON 'auto'`. However, this doesn't work for the events due to using different uppercase/lowercase letters in the JSON keys and staging tables. Instead, we need to specify a mapping JSON file `JSON 's3://udacity-dend/log_json_path.json'` provided by the guidelines.

I set `COMPUPDATE OFF` because it might make the loading a bit faster compared to the querying later on. But in our case, loading is definitely the bottleneck. All other values are default values.

### Load step

Loading the data from the staging tables into the final database is often rather simple, see command below

```sql
INSERT INTO artists (artist_id, name, location, latitude, longitude)
SELECT DISTINCT artist_id, artist_name, artist_location, artist_latitude, artist_longitude
FROM song_stage_table;
```

Only a few commands need more explanation

- `TIMESTAMP 'epoch' + ts/1000 * INTERVAL '1 second' AS start_time,`
  - this command converts the `ts` UNIX timestamp from milliseconds to seconds, then converts it to an `INTERVAL` object and finally adds it to the Unix epoch timestamp (1.1.1970)
- `WHERE e.page = 'NextSong';`
  - This was mentioned in the guidelines. Only some events are actually relvant to playing songs (6820 times). Others events represent the user going to the homepage (806 times), logging in or logging out (both around 90 times) or opening settings, help, about or upgrade page.


## Provide example queries and results for song play analysis

### Top 10 songs

```sql
SELECT s.title, a.name, COUNT(*) AS play_count
FROM songplays sp
JOIN songs s ON sp.song_id = s.song_id
JOIN artists a ON sp.artist_id = a.artist_id
GROUP BY s.title, a.name
ORDER BY play_count DESC
LIMIT 10;
```

```
[RealDictRow([('title', "You're The One"),
              ('name', 'Dwight Yoakam'),
              ('play_count', 37)]),
 RealDictRow([('title', 'Catch You Baby (Steve Pitron & Max Sanna Radio Edit)'),
              ('name', 'Lonnie Gordon'),
              ('play_count', 9)]),
 RealDictRow([('title', "I CAN'T GET STARTED"),
              ('name', 'Ron Carter'),
              ('play_count', 9)]),
 RealDictRow([('title', "Nothin' On You [feat. Bruno Mars] (Album Version)"),
              ('name', 'B.o.B'),
              ('play_count', 8)]),
 RealDictRow([('title', "Hey Daddy (Daddy's Home)"),
              ('name', 'Usher featuring Jermaine Dupri'),
              ('play_count', 6)]),
 RealDictRow([('title', "Hey Daddy (Daddy's Home)"),
              ('name', 'Usher'),
              ('play_count', 6)]),
 RealDictRow([('title', 'Up Up & Away'),
              ('name', 'Kid Cudi'),
              ('play_count', 5)]),
 RealDictRow([('title', 'Make Her Say'),
              ('name', 'Kid Cudi / Kanye West / Common'),
              ('play_count', 5)]),
 RealDictRow([('title', 'Up Up & Away'),
              ('name', 'Kid Cudi / Kanye West / Common'),
              ('play_count', 5)]),
 RealDictRow([('title', 'Make Her Say'),
              ('name', 'Kid Cudi'),
              ('play_count', 5)])]
```

### Number of active users per week

```sql
SELECT t.week, COUNT(DISTINCT sp.user_id) AS active_users
FROM songplays sp
JOIN time t ON sp.start_time = t.start_time
GROUP BY t.week
ORDER BY t.week;
```

```
[RealDictRow([('week', 44), ('active_users', 13)]),
 RealDictRow([('week', 45), ('active_users', 27)]),
 RealDictRow([('week', 46), ('active_users', 26)]),
 RealDictRow([('week', 47), ('active_users', 25)]),
 RealDictRow([('week', 48), ('active_users', 24)])]
```

### Gender distribution of users

```sql
SELECT u.gender, COUNT(*) AS user_count
FROM users u
GROUP BY u.gender;
```

```
[RealDictRow([('gender', 'M'), ('user_count', 45)]),
 RealDictRow([('gender', 'F'), ('user_count', 60)])]
```