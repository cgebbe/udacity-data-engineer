- [Introduction](#introduction)
  - [Intro](#intro)
  - [Exercise PostgreSQL](#exercise-postgresql)
    - [Setup](#setup)
    - [Content](#content)
  - [NoSQL databases](#nosql-databases)
  - [Exercise Apache Cassandra](#exercise-apache-cassandra)
    - [Setup](#setup-1)
    - [Content](#content-1)
  - [Review](#review)
- [Relational Data Model](#relational-data-model)


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

## Review

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