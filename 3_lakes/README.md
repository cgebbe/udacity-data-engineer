# Spark and data lakes

- [Spark and data lakes](#spark-and-data-lakes)
- [Intro](#intro)
- [Spark Essentials](#spark-essentials)
- [Using Spark in AWS](#using-spark-in-aws)
- [Lakehouse architecture](#lakehouse-architecture)

FYI: All exercises are available here: https://github.com/udacity/nd027-Data-Engineering-Data-Lakes-AWS-Exercises

# Intro

Big data ecosystem

- early effort: Hadoop ecoystem (from Apache), consisting of...
  - Hadoop Distributed File System (HDFS) = file storage system
  - MapReduce = parallel processing system
  - Hadoop YARN = resource manager for scheduling jobs
  - Apache Pig = SQL like language on top of MapReduce
  - Apache Hive = another SQL like interface on MapReduce
- next step: Apache Spark
- final step: lakehouse (wanting to combine strength)

Spark

- Spark often faster than Hadoop because keeps everything in memory (while Hadoop writes intermediate results to disk)
- Spark can work on HDFS but also sources (file systems, databases, streaming systems)
- Streaming: rather special (spark streaming, storm, flink)
- can be setup in 4 modes:
  - local mode (only one node)
  - Spark Standalone Customer Manager
  - Hadoop YARN
  - Open Source Manager from UC Berkley AMPLab
- Spark shell interacts with driver process to schedule task

When to use spark

- NOT when using small data
- NOT when having a relational database anyhow ?!
- NOT when streaming and latency < 500ms is important
- NOT when using deep learning (at least not natively)?!

Alternatives to Spark

- new databases: HBase, Cassandra
- distributed SQL engines: Impala, Presto

Data Lake

- PRO
  - supports structured, semi-structured and unstructured data
  - provides "schema-on-read" versus "schema-on-write"
  - have lower costs (?)
- CON
  - no atomic transactions
  - no quality enforcement
  - inconsistent data structures

Lakehouse

- key innovation: creation of metadata and governance layer
- also allows to incrementally improve data quality
  - bronze = raw data
  - silver = filtered, cleaned, augmented
  - gold = added business-level aggregate (star-schema)

# Spark Essentials

- important to write idempotent code (~functional, avoiding side effects)
- DO NOT read data into lists, instead use native APIs such as RDD
- spark uses lazy evaluation by default, creates DAG, optimizes it (using "Catalyst")
- spark treats data as immutable

APIs

- Resilient Distributed Dataset (RDD)
  - =collection of elements
  - only one in beginning
  - rather low-level
  - useful if data is unstructured
- DataFrame
  - = table with named columns (but no types?! not sure...)
  - higher level
  - introduces tables with columns!
- Datasets
  - = collection of strongly typed JVM objects (Java VM)
  - most restrictive
  - adds additional compile checks
- image.png

![](README.assets/2023-05-10-00-09-10.png)

PySpark

- SparkContext - connects to cluster
- SparkSession
- Exercise
  - load a simple list of strings as **RDD** (`SparkContext.parallelize`)
  - `map` a function to it
  - `collect` results

Filesystem

- Spark may use HDFS files
- such files may be replicated
- and stored in blob storage

Exercise Spark DataFrames

- `df=spark.read.json(path)`
- `df.write.save(out_path, format='csv')`
- other relevant methods
  - info
    - printSchema()
    - describe()
  - general
    - select
    - take = head
    - filter = where
    - sort
    - dropDuplicates
    - withColumn - adds/updates column
  - aggregate
    - groupBy
    - agg({"salary": "avg", "age": "max"})
    - count
    - countDistinct
    - avg,max,min
  - window functions
    - partitionBy
    - rangeBetween
    - rowsBetween
  - udf
    - see below

```python
get_hour = udf(lambda x: datetime.datetime.fromtimestamp(x / 1000.0). hour)
user_log = user_log.withColumn("hour", get_hour(user_log.ts))
```

SparkSQL

- is declarative approach (contrasting with procedural above)
- example below

```python
spark.sql('''
          SELECT userID, firstname, page, song
          FROM user_log_table
          WHERE userID == '1046'
          '''
          ).collect()
```

# Using Spark in AWS

- There are several options to run Spark in AWS
  - AWS EMR = Elastic MapReduce
    - supports Apache Spark, Hadoop, Hive and Prestor
  - EC2 (would need to install Spark on each machine)
  - Glue
    - needs some setup since S3 runs in different network?!
    - Exercise: Use mostly CLI to create Glue and required services

![](README.assets/2023-05-11-20-40-25.png)
![](README.assets/2023-05-11-21-49-58.png)

- choosing storage system

  - here: S3 for simplicity and costs
  - better: HDFS
    - HDFS replicates and is thus fault-tolerant
    - therefore, Spark often installed on top of Hadoop(?)
    - HDFS requires strict fileformat: parquet or avro

- Glue Jobs
  - scheduled jobs
  - can be created as python files and uploaded
  - can be created via drag/drop in Glue Studio consisting of
    - https://docs.aws.amazon.com/glue/latest/dg/tables-described.html
    - source (S3, glue table, databases)
    - transform
    - target
  - Exercise in GlueStudio: run once
    - source=`aws s3 cp ./project/starter/customer/customer-1655563258079.json s3://_______/customer/landing/`
    - transform = filter `shareWithResearch!=0`
    - destination = `.../customer/trusted`
    - export as python script, see
      - https://github.com/udacity/nd027-Data-Engineering-Data-Lakes-AWS-Exercises/tree/main/lesson-3-using-spark-in-aws/exercises/concept3-creating-a-job-using-glue-studio/solution

# Lakehouse architecture

- recommendations
  - uses several zones
    - landing zone (raw)
    - trusted zone (validated, maybe cleaned)
    - curated (e.g. joining daa)
  - use compression (gzip) to reduce S3 costs
  - store in columnar format e.g. parquet

AWS Glue Data Catalog (used to stored metadata)

- open source alternatives
  - Apache Hive Metastore (built on Hadoop)
    - primarily designed for Apache Hive data warehouse
  - Apache Atlas
    - more unified for various platforms
  - Apache Range
    - more security focused, provides access control
  - Alation (paid)
  - Collibra (paid)
- cloud alternatives
  - AWS Glue Data Catalog
  - AWS Lake Formation - offers more than cataloging
  - Azure Purview
  - Azure Data Catalog

Glue tables

- like pointer to original table (only structured data)
- plus metadata (schema)
- can be used like a symlink to access data
- can be defined in various ways
  - Glue console = UI (defining each field)
  - Glue job can generate table definition automatically
  - SQL using Data Definition Language (DDL) or CREATE
- once setup, can use AWS Athena
  - serverless SQL query tool
  - designed to query data in S3 (JSON, Parquet, ORC, etc.)
- _Exercise: Created landing zone_
  - copy into landing zone `aws s3 cp ./project/starter/accelerometer/ \ s3://_______/accelerometer/landing/ --recursive`
  - create Glue table using Glue Console
  - Run Athena (What is happening here?!)
  - save query output as `*_landing.sql`

Data Privacy

- recommendation: use opt-in flag for each customer (whether data usage allowed)
- Problem: Often secondary data recorded in different tables (website clicks, chat history, etc.)
  - Solution: JOIN secondary data with customeTable to check allowance
  - _Exercise: create trusted zone_
  - JOIN accelerometer node with customer node
  - DROP some rows
  - save output in trusted zone

Streaming

- Spark Streaming for near real-time data receiving
- possible message brokers
  - Kafka
  - AWS SQS (Simple Queue Service)
  - Amazon Kinesis
- Glue can load data directly from Kafka and Kinesis
- Alternatively, Kafka (+x?) can store directly in S3

Curated data

- _Exercise: Curated data_
  - Clone previous job for trusted zone
  - add `DropFields` transform dropping accelormeter fields (?!)
