# Spark and data lakes

- [Spark and data lakes](#spark-and-data-lakes)
- [Intro](#intro)
- [Spark Essentials](#spark-essentials)
- [Using Spark in AWS](#using-spark-in-aws)
- [Lakehouse architecture](#lakehouse-architecture)
- [Project STEDI Step Trainer](#project-stedi-step-trainer)
  - [Instructions](#instructions)
  - [Rubrik](#rubrik)
  - [Data](#data)
  - [TODO internal](#todo-internal)
  - [Lessons learned](#lessons-learned)
  - [Solutions from other students](#solutions-from-other-students)

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

# Project STEDI Step Trainer

## Instructions

To simulate the data coming from the various sources, you will need to

- [x] create your own S3 directories for customer_landing, step_trainer_landing, and accelerometer_landing zones, and
- [x] copy the data there as a starting point.

- [x] You have decided you want to get a feel for the data you are dealing with in a semi-structured format, so you decide to _create two Glue tables for the two landing zones_. Share your `customer_landing.sql` and your `accelerometer_landing.sql` script in git.
- [x] _Query those tables_ using Athena, and take a screenshot of each one showing the resulting data. Name the screenshots `customer_landing(.png`,.jpeg, etc.) and `accelerometer_landing(.png`,.jpeg, etc.).

The Data Science team has done some preliminary data analysis and determined that the Accelerometer Records each match one of the Customer Records. They would like you to create two AWS Glue Jobs (using Glue studio) that do the following:

- [x] Sanitize the _Customer data_ from the Website (Landing Zone) and only store the Customer Records who agreed to _share their data for research purposes_ (Trusted Zone) - creating a Glue Table called customer_trusted.
  - customer
    - landing 999
    - trusted 497
  - accelerometer
    - landing 744413
    - trusted 413460 (veri fied through manual SQL statement)
- [x] Sanitize the _Accelerometer data_ from the Mobile App (Landing Zone) - and only store Accelerometer Readings from customers who agreed to share their data for _research purposes_ (Trusted Zone) - creating a Glue Table called accelerometer_trusted.
- [x] You need to verify your Glue job is successful and only contains Customer Records from people who agreed to share their data. Query your Glue customer_trusted table with Athena and take a screenshot of the data. Name the screenshot customer_trusted(.png,.jpeg, etc.).

Data Scientists have discovered a data quality issue with the Customer Data. The serial number should be a unique identifier for the STEDI Step Trainer they purchased. However, there was a defect in the fulfillment website, and it used the same 30 serial numbers over and over again for millions of customers! Most customers have not received their Step Trainers yet, but those who have, are submitting Step Trainer data over the IoT network (Landing Zone). The data from the Step Trainer Records has the correct serial numbers.

The problem is that because of this serial number bug in the fulfillment data (Landing Zone), we don’t know which customer the Step Trainer Records data belongs to. The Data Science team would like you to write a Glue job that does the following:

- Sanitize the Customer data (Trusted Zone) and create a Glue Table (Curated Zone) that only includes customers who have accelerometer data and have agreed to share their data for research called customers_curated.

Finally, you need to create two Glue Studio jobs that do the following tasks:

- Read the Step Trainer IoT data stream (S3) and populate a Trusted Zone Glue Table called step_trainer_trusted that contains the Step Trainer Records data for customers who have accelerometer data and have agreed to share their data for research (customers_curated).
- Create an aggregated table that has each of the Step Trainer Readings, and the associated accelerometer reading data for the same timestamp, but only for customers who have agreed to share their data, and make a glue table called machine_learning_curated.

## Rubrik

https://review.udacity.com/#!/rubrics/4883/view

## Data

Three JSON files

- customer records
- step trainer records
- accelormeter records

## TODO internal

- [x] setup infrastructure
  - could do manually, but would highly prefer Terraform
- [x] copy stuff to S3 (AW CLI)
  - simply via AWS CLI
- [x] create SQL DDL scripts to create Glue tables
  - customer_landing.sql
  - accelerometer_landing.sql
  - this also checks whether my VPC-endpoint is setup correctly!
- [x] run these script
- [x] query tables using Athena

## Lessons learned

Glue ecoystem

- glue job
  - serverless data processing service
  - requires an IAM role for e.g. S3 access
- glue crawler
  - = automated data discover service for glue data catalog
  - infers schemas and creates metadata tables
- glue connection
  - defines connection to (usually external?) data source
- glue registry
  - stores and versions schemas and transformations
  - provides additional functionality to glue data catalog
- glue studio
  - visual interface for building and running glue ETL jobs

Why VPC endpoint, route table, etc. is necessary

- still not 100% clear, i think in this case bogus...
- AWS Glue jobs are serverless and run by default "outside" any VPC
- AWS Glue jobs _might_ need to run inside VPC wout internet access
  - for e.g. databases
  - for NAT gateways, Elastic IPs
  - ...?
- In such a case
  - VPC endpoint
    - enables communication between private VPC and other AWS services
    - When executing AWS Glue jobs, one selects a VPC!
  - route table
    - directs traffic to VPC endpoint
- Sidenote: EC2 can access S3 buckets if EC2 has internet access

How to run SQL DDL script?

- running dummy jobs on AWS Studio with IAM policy works
- Hmm... this is surprisingly tricky?!
- https://docs.aws.amazon.com/glue/latest/dg/tables-described.html
- Apparently need to use AWS Athena for this
  - Athena = serverless query service for data stored in S3
  - Athena integrates Glue Data Catalog

How to run AWS Glue locally

- https://docs.aws.amazon.com/glue/latest/dg/aws-glue-programming-etl-libraries.html#develop-local-python
- https://github.com/awslabs/aws-glue-libs/issues/3#issuecomment-1145339126

```bash
docker run -it --rm \
-v ~/.aws:/home/glue_user/.aws \
-v /mnt:/mnt \
-e AWS_PROFILE=default \
-e DISABLE_SSL=true \
-p 4040:4040 -p 18080:18080 -p 8998:8998 -p 8888:8888 \
--name glue_jupyter_lab \
amazon/aws-glue-libs:glue_libs_4.0.0_image_01 \
/home/glue_user/jupyter/jupyter_start.sh
```

Why did Filter not work?

- likely it did not work because of Null values in column
- Filter preview doesn't output any rows, tried all conditions

AWS Glue `DynamicDataFrame` appends by default (instead of overwriting)

- there are only workarounds requiring to go to script mode
  - either add command to purge S3 path
  - or convert to PySpark Dataframe (instead of Glue Dynamic Frame)
  - see https://stackoverflow.com/q/52001781/2135504

## Solutions from other students

- https://github.com/Lal4Tech/Data-Engineering-With-AWS/tree/main/3_Spark_and_Data_Lakes/project
