- [Introduction](#introduction)
  - [Intro](#intro)
  - [Exercise PostgreSQL](#exercise-postgresql)
    - [Setup](#setup)
    - [Content](#content)
  - [NoSQL databases](#nosql-databases)
  - [Exercise Apache Cassandra](#exercise-apache-cassandra)
    - [Setup](#setup-1)
    - [Content](#content-1)
  - [Conclusion](#conclusion)
- [Relational Data Model](#relational-data-model)
  - [Conclusion](#conclusion-1)
- [NoSQL data models](#nosql-data-models)
  - [Exercises Cassandra](#exercises-cassandra)
  - [Conclusion](#conclusion-2)
- [Project: Data Modeling with Cassandra](#project-data-modeling-with-cassandra)
  - [Lessons learned](#lessons-learned)


# Introduction

## Intro 

- what is data modeling?
- column = attribute
- can you join two arbitraty tables?
- ACID = ...
- PostgreSQL = ...
- difference database and table

## Exercise PostgreSQL 

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

## NoSQL databases

- Apache Cassandra (Partition Row store) <-- used in this course
- MongoDB (Document store)
- DynamoDB (Key-Value store)
- Apache HBase (Wide Column Store)
- Neo4J (Graph Database)

Infos
- keyspace = database
- Apache Cassandra uses CQL, which is very similar to SQL

When to use NoSQL 
- store different types of data
- large amounts of data, higher availability (via horizontal scalability)
- higher throughput (by relaxing ACID - although eg. MongoDB 4.0 offers ACID)
- flexible schema (different columns for every row)

When not to use
- prefer ACID
- need to use JOINS across tables

## Exercise Apache Cassandra

### Setup 

```bash
# https://cassandra.apache.org/doc/latest/cassandra/getting_started/installing.html
sudo apt-get install cassandra

# screw that, doesn't work, use docker, see https://cassandra.apache.org/_/quickstart.html
docker run --rm -it -p 9042:9042 -p 7199:7199 cassandra:latest
```

### Content

- partition key allows WHERE statement !
- primary key needs to be unique (year, artist_name) !
- partition key part of primary key?!


Data modeling according to ChatGPT
- identify entitites (e.g. person, thing, concept)
- define attributes (=columns)
- determine relationships
- normalize data = organize into tables (goal: reduce redundancy)
- create data model = visualize tables and relationships

## Conclusion

- What Data Modeling is
- Stakeholders involved in Data Modeling
- When to use Relational Databases
- When not to use Relational Databases
- When to use NoSQL Databases
- When not to use NoSQL Databases
- How to create tables and insert data into PostgreSQL
- How to create tables and insert data into Apache Cassandra

# Relational Data Model

- OLAP vs OLTP (analytical vs. transactional)
- normalization (first, second, third) normal form
  - 1NF = no arrays
  - 2NF = non-key columns depend on ENTIRE primary key
  - 3NF = non-key columns ONLY depend on primar key (not any other non-key column, i.e. 'transitive' dependency)
- denormalization
  - problem: normalization great for consistency and removing redundancy but requires slow JOINs
  - solution: denormalize for speedup

- Fact table = main data, many rows/transactions, foreign keys to dim tables
- dimension tables = descriptibe information, usually much smaller
- Star schema (denormalized, one central fact table) vs snowflake schema (more normalized, usually 1NF or 2NF)
  - see https://bluepi-in.medium.com/deep-diving-in-the-world-of-data-warehousing-78c0d52f49a

- when creating tables and specifying dtypes..
  - `int NOT NULL` doesn't allow empty fields
  - `UNIQUE`
  - `PRIMARY KEY` = can be one or several cols (then called composite key). Also, implies NULL and UNIQUE
- special actions
  - `UPSERT` = insert or update row
  - `INSERT`
  - can be combined with `ON CONFLICT DO NOTHING` or `ON CONFLICT DO UPDATE`

## Conclusion
- Codd’s 12 guidelines of relational database design
- OLAP and OLTP
- database normalization, normal forms, denormalization
- Fact vs. dimension tables
- star and snowflake schema

# NoSQL data models

- eventual consistency
- CAP = any data store can only provide 2/3 features
  - Consistency = all nodes see same data
  - Availability = responds to every request (somewhat quick?)
  - Partition tolerance (against lost connectivity between nodes)
- Apache Cassandra supports Availabily and partition tolerance, but only eventual consistency


- Cassandra does not support JOINS. One query can only access one table. Therefore,..
  - denormalization !!! -> model data for queries (many new tables)
  - secondary indexes
  - collections
  - user-defined-functions (UDF)
  - materialized views
- CQL like SQL without JOINS, GROUP-BY, subqueries

## Exercises Cassandra

- `WHERE`
  - can only be used on PRIMARY KEY
  - with `ALLOW FILTERING` on all columns, but results in full scan (inefficient!)
  - should be used in every query (unless you really want all data)
- **partition key**
  - = part of primary key deciding how data is partitioned
  - only exists in NoSQL dbs? At least only distributed dbs...
  - can also be a composite (but we didn't discuss this in lecture)
- **primary key**
  - = partition key + optionally several clustering columns
  - must be unique (if not unique, queries return only one row)
- **clustering col**
  - = for sorting and ranged queries (ascending by default)
  - should be used in order when SELECT ?!
  - partition key NOT used 

```sql
-- note that album_name is primary_key AND clustering column
CREATE TABLE IF NOT EXISTS music_library
(year int, artist_name text, album_name text, city text, PRIMARY KEY (artist_name, album_name, city))"
```

## Conclusion

- no JOIN, so model tables for your queries!
- Primary Key, Partition Key, and Clustering Column
- WHERE only on primary key (or inefficiently on all)

# Project: Data Modeling with Cassandra

- Task:
  - Given some queries in natural language, setup an appropriate cassandra data model
  - Then, transfer several CSV files via ETL into database
- Technical details
  - can only be done in their project
  - need to setup DNS over cloudflare, see https://udacity.zendesk.com/hc/en-us/articles/115004653246?input_string=workspace+not+loading


## Lessons learned

- Why not everything a clustering column?
  - clustering columns not really efficient for filtering ?!
  - think of partition key and clustering cols as nested sorted map
    - https://tech.ebayinc.com/engineering/cassandra-data-modeling-best-practices-part-1/
