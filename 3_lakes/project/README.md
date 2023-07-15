# Project STEDI Step Trainer

## Instructions

To simulate the data coming from the various sources, you will need to

- [x] create your own S3 directories for customer_landing, step_trainer_landing, and accelerometer_landing zones, and
- [x] copy the data there as a starting point.

- [x] You have decided you want to get a feel for the data you are dealing with in a semi-structured format, so you decide to _create two Glue tables for the two landing zones_. Share your `customer_landing.sql` and your `accelerometer_landing.sql` script in git.
- [x] _Query those tables_ using Athena, and take a screenshot of each one showing the resulting data. Name the screenshots `customer_landing(.png`,.jpeg, etc.) and `accelerometer_landing(.png`,.jpeg, etc.).

The Data Science team has done some preliminary data analysis and determined that the Accelerometer Records each match one of the Customer Records. They would like you to create two AWS Glue Jobs (using Glue studio) that do the following:

- [x] Sanitize the Customer data from the Website (Landing Zone) and only store the Customer Records who agreed to _share their data for research purposes_ (Trusted Zone) - creating a Glue Table called **customer_trusted**.

```sql
-- customer-landing: 999
-- customer-trusted: 497
-- customer-trusted-wout-duplicates: 497

```

- [x] Sanitize the Accelerometer data from the Mobile App (Landing Zone) - and only store Accelerometer Readings from customers who agreed to _share their data for research purposes_ (Trusted Zone) - creating a Glue Table called **accelerometer_trusted**.

- accelerometer

  - landing 744413
  - trusted 413460 (veri fied through manual SQL statement)

- [x] You need to verify your Glue job is successful and only contains Customer Records from people who agreed to share their data. Query your Glue customer_trusted table with Athena and take a **screenshot** of the data. Name the screenshot customer_trusted(.png,.jpeg, etc.).

Data Scientists have discovered a data quality issue with the Customer Data. The serial number should be a unique identifier for the STEDI Step Trainer they purchased. However, there was a defect in the fulfillment website, and it used the same 30 serial numbers over and over again for millions of customers! Most customers have not received their Step Trainers yet, but those who have, are submitting Step Trainer data over the IoT network (Landing Zone). The data from the Step Trainer Records has the correct serial numbers.

Because of this serial number bug in the fulfillment data (Landing Zone), we don’t know which customer the Step Trainer Records data belongs to. The Data Science team would like you to write a Glue job that does the following:

- [x] Sanitize the Customer data (Trusted Zone) and create a Glue Table (Curated Zone) that only includes _customers who have accelerometer data_ and have agreed to share their data for research called **customers_curated**.
  - NOTE: This should also yield 497 rows given SQL statement below!

```sql
-- customer_curated: 497 (query below)
SELECT COUNT(*)
FROM "customer_trusted"
WHERE email in (SELECT "user" from "accelerometer_trusted")
```

Finally, you need to create two Glue Studio jobs that do the following tasks:

- [x] Read the Step Trainer IoT data stream (S3) and populate a Trusted Zone Glue Table called **step_trainer_trusted** that contains the Step Trainer Records data for customers who have accelerometer data and have agreed to share their data for research (_customers_curated_).

```sql
-- step-trainer-landing: 239760
-- step-trainer-curated: 29970 (query below)
SELECT COUNT(*)
FROM "step_trainer_landing"
WHERE "serialnumber" in (SELECT "serialnumber" from "customer_curated")
-- LEFT JOIN "customer_curated" ON "customer_curated"."serialnumber" = "step_trainer_landing"."serialnumber"
LIMIT 10
```

- [x] Create an aggregated table that has each of the Step Trainer Readings, and the associated accelerometer reading data for the same timestamp, but only for customers who have agreed to share their data, and make a glue table called **machine_learning_curated**.

```sql
-- machine_learning_curated: 3357 (query below).
-- WARNING: Has several rows with same timestamp due to duplicates in accel and customer!
SELECT *
FROM customer_trusted
INNER JOIN accelerometer_trusted ON customer_trusted.email = accelerometer_trusted.user
INNER JOIN step_trainer_curated ON customer_trusted.serialnumber = step_trainer_curated.serialnumber
WHERE accelerometer_trusted.timestamp = step_trainer_curated.sensorreadingtime
LIMIT 10
```

- **INTERIM TASK: check duplicates**
  - customer.email
  - (accel.user, accel.timestamp)
  - (trainer.sensorReadingTime, trainer.serialnumbe)

```sql
-- yep, many duplicates (at most 6 for AngelDavis and LarryMitra)
SELECT email, COUNT(*) AS duplicate_count
FROM customer_landing
GROUP BY email
ORDER BY duplicate_count DESC;

-- accelerometer also has a lot of duplicates (at most 6)
SELECT accelerometer_landing.user, accelerometer_landing.timestamp, COUNT(*) AS duplicate_count
FROM accelerometer_landing
GROUP BY accelerometer_landing.user, accelerometer_landing.timestamp
ORDER BY duplicate_count DESC;

-- step_trainer has few duplicates (5 rows with duplicate_count 2)
SELECT sensorreadingtime, serialnumber, COUNT(*) AS duplicate_count
FROM step_trainer_landing
GROUP BY sensorreadingtime, serialnumber
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;
```

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
