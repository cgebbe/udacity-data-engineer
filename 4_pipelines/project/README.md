# Project: Data Pipelines with Airflow

Goal: Move JSON logs and metadata from S3 to Amazon Redshift

![](README.assets/2023-07-16-21-04-04.png)

## Details

custom operators to perform tasks such as

- staging the data
- filling the data warehouse
- running checks on the data as the final step.

You'll be provided with a helpers class that contains all the SQL transformations. Thus, you won't need to write the ETL yourselves, but you'll need to execute it with your custom operators.

## How to setup environment

from lesson "Airflow and AWS"

- [x] `Create an IAM User in AWS`

```python
# Use S3 inside airflow
from airflow.hooks.S3_hook import S3Hook

hook = S3Hook(aws_conn_id='aws_credentials')
        bucket = Variable.get('s3_bucket')
        prefix = Variable.get('s3_prefix')
        logging.info(f"Listing Keys from {bucket}/{prefix}")
        keys = hook.list_keys(bucket, prefix=prefix)
        for key in keys:
            logging.info(f"- s3://{bucket}/{key}")
    list_keys()

list_keys_dag = list_keys()
```

- [ ] `Configure Redshift Serverless`
- [ ] Connect Airflow and AWS: `Connections - AWS Credentials`
- [ ] `Add Airflow Connections to AWS Redshift`

- airflow
  - use the one provided by Udacity
  - OR use local airflow and [project template](https://s3.amazonaws.com/video.udacity-data.com/topher/2019/February/5c6058dc_project-template/project-template.zip) containing
    - DAG template with imports
    - operators
    - helper classes with SQL transformations

## Instructions

- [ ] start airflow

```bash
# check if already running
ps aux | grep airflow

# to start Postgres and Cassandra
source /opt/airflow/start-services.sh

# to start airflow
source /opt/airflow/start.sh

# to connect
cd /home/workspaces
chmod +x set_connections_and_variables.sh
source ./set_connections_and_variables.sh

# add admin user
airflow users create --email student@example.com --firstname aStudent --lastname aStudent --password admin --role Admin --username admin

# check again
ps aux | grep airflow
```

- [ ] copy to own S3 bucket
  - Log data: s3://udacity-dend/log_data
  - Song data: s3://udacity-dend/song_data

```bash
aws s3 cp s3://udacity-dend/log-data/ ~/log-data/ --recursive
aws s3 cp ~/log-data/ s3://<my_bucket>/log-data/ --recursive
aws s3 ls s3://sean-murdock/log-data/
```

- [ ] add default parameters according to these guidelines

  - The DAG does not have dependencies on past runs
  - On failure, the task are retried 3 times
  - Retries happen every 5 minutes
  - Catchup is turned off
  - Do not email on retry

- [ ] configure task dependencies s.t. below

![](README.assets/2023-07-16-21-15-09.png)

- [ ] build Stage operator
  - loads JSON from S3 to Redshift staging
  - inputs
    - s3-path
    - redshift-table-name
- [ ] build Fact and Dimension operator
  - inputs
    - SQL statement
    - source table name
    - target table name
    - insert_mode = {overwrite (truncate-insert), append}
      - overwrite for dimension tables
      - append for fact tables (because so long)
- [ ] build Data Quality operator
  - inputs
    - SQL test statement
    - expected test result

## FAQs

Missing time table schema

```sql
CREATE TABLE public.time (
    start_time timestamp NOT NULL,
    hour int4 NOT NULL,
    day int4 NOT NULL,
    week int4 NOT NULL,
    month int4 NOT NULL,
    year int4 NOT NULL,
    dayofweek int4 NOT NULL,
);
```

Staging should be scheduled hourly ?!

Load into staging

> You need to use the /log_json_path.json file to specify the format of the json file for the log data (and use the 'auto' setting for song data)
