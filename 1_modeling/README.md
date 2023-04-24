- [Introduction](#introduction)
  - [Intro](#intro)
  - [Exercise](#exercise)
    - [Setup](#setup)
    - [Content](#content)


# Introduction

## Intro 

- what is data modeling?
- column = attribute
- can you join two arbitraty tables?
- ACID = ...
- PostgreSQL = ...
- difference database and table

## Exercise

### Setup

- apt install postgresql
- setup user and db via `sudo postgres` CLI tool
- pip install psycopg2

```bash
# install postgres
sudo apt-get install postgresql postgresql-contrib
sudo service postgresql start

# to setup user and database
sudo -u postgres psql
CREATE DATABASE studentdb;
CREATE USER student WITH PASSWORD 'student';
GRANT ALL PRIVILEGES ON DATABASE studentdb TO student;
\q

# likely config
sudo nano /etc/postgresql/[version]/main/pg_hba.conf
local   all             all                                     password

# test
psql -U student -d studentdb
CREATE TABLE test (id serial PRIMARY KEY, name VARCHAR(50));
INSERT INTO test (name) VALUES ('John'), ('Mary'), ('Bob');
SELECT * FROM test;
```


### Content

- start connection and cursor
- CREATE database and table
- INSERT and SELECT data
- DROP table
