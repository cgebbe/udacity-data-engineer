# Data pipelines

see code at https://github.com/cgebbe/cd0031-automate-data-pipelines (couldn't find original repo in https://github.com/orgs/udacity/repositories, pushed from Udacity workspace)

## Intro

- DAG
- airflow
- ...

How to use airflow in workspace

- spawns automatically printing `[INFO] Listening at: http://0.0.0.0:8793 (448)`
- to access, click on `ACCESS AIRFLOW` and (admin,admin)
- to install requirements `pip install -r requirements`
  - contains `apache-airflow-providers-postgres` and `apache-airflow`
  -

## Data Pipelines

### Simple pipeline

```python
# Simple DAG pipeline
import logging
import pendulum
from airflow.decorators import dag, task

@dag(start_date=pendulum.now(), schedule_interval="@daily")
def flow_dag():

    @task
    def hello():
        logging.info("Hello World!")

    hello()

# NOTE: calling DAG and assigning to value somehow required?!
dag=flow_dag()
```

### Airflow Components

- Worker
- work queue
- scheduler
- metadata store (credentials, history, task state, ...)
- web interface for UI

## Operators

- > Operators define the atomic steps of work that make up a DAG
- > Instantiated operators are referred to as Tasks.

- Examples
  - PythonOperator
  - PostgresOperator
  - RedshiftToS3Operator
  - S3ToRedshiftOperator
  - BashOperator
  - SimpleHttpOperator
  - Sensor
- **Benefits of operators**
  - has pre-built functionality from airflow or third party
  - higher abstraction, faster to get results

```python
def hello_world():
    print(“Hello World”)

divvy_dag = DAG(...)
task = PythonOperator(
    task_id=’hello_world’,
    python_callable=hello_world,
    dag=divvy_dag)
```

### Task dependencies

- airflow does NOT determine dependencies automatically (like e.g. kubeflow)
- Two options
  - "big shift" operator `>>`, e.g. `task1 >> task2`
  - `set_upstream` or `set_downstream` functions, e.g. `task1.set_downstream(task2)`

```python
import pendulum
from airflow.decorators import dag, task

@dag(schedule_interval='@hourly', start_date=pendulum.now())
def task_dependencies():

    @task()
    def addition(first,second):
        return first+second

    @task()
    def division(first,second):
        return first/second

    add1= addition(5,5)
    add2 = addition(1,4)
    final = division(add1,add2)

    add1 >> final
    add2 >> final

task_dependencies_dag=task_dependencies()
```

## Hooks

- Benefits of Hooks
  - provide reusable interface to external systems / databases
  - stores credentials (somewhere?)
  - = higher abstraction

```python

from airflow import DAG
from airflow.hooks.postgres_hook import PostgresHook
from airflow.operators.python_operator import PythonOperator

def load():
    # Create a PostgresHook option using the `demo` connection
    db_hook = PostgresHook(‘demo’)
    df = db_hook.get_pandas_df('SELECT * FROM rides')
    print(f'Successfully used PostgresHook to return {len(df)} records')

load_task = PythonOperator(task_id=’load’,python_callable=hello_world)
```

### Templates

- to use runtime parameters
  - `{{ds}}` = date of run
  - `{{run_id}}`
  - `{{next_execution_date}}`
  - ...
- see https://airflow.apache.org/docs/apache-airflow/stable/templates-ref.html

```python
from airflow.decorators import dag, task

@dag(schedule_interval="@daily")
def template_dag(**kwargs):
  @task
  def hello_date():
    print(f“Hello {kwargs['ds']}}”)

```

## Airflow and AWS

- NOTE

  - AWS provides managed airflow, see https://aws.amazon.com/managed-workflows-for-apache-airflow/
  - Here, we use airflow setup from udacity via notebooks :/

- Configure AWS IAM
- Configure AWS Redshift Serverless
- Configure AWS S3
  - uses example data from `s3://udacity-dend/data-pipelines/`
- Connect Airflow to AWS using IAM credentials
- Connect Airflow to AWS Redshift Serverless
- Connect Airflow to AWS S3
- Query Redshift data using AWS Console

## Data Quality

- data lineage
  - for them the DAG is the lineage, WTF?!
- scheduling
  - if start_date in the past, airflow will "catch up", i.e. create "historical" runs
  - useful if e.g. daily run only processes data from previous day
  - use `{{execution_date}}` to get simulated date
- partitioning
  - = splitting a large workload into smaller parts called partitions
  - see above, e.g. using `{{execution_date}}`
  - benefits
    - easier to debug due to samller data
    - potentially fewer dependencies
  - partitioning can happen by
    - time
    - location
    - size
    - logic (?!)
- data quality
  - example requirements
    - minimum size
    - accurate within some error margin
    - arrive timely
    - anonymized / insensitive data
    - ...
  - their solution: add check task to check records
-

```python
# EXAMPLE: catchup feature from airflow
@dag(
    schedule_interval='@daily',
    start_date=pendulum.now(),
    catchup=False,  # WARNING: True by default!
    max_active_runs=1,
)
```

## Production Data Pipelines

<!-- - Focus on elevating your DAGs to reliable, production-quality data pipelines.
- Extending airflow with custom plug-ins to create your own hooks and operators.
- How to design task boundaries so that we maximize visibility into our tasks.
- subDAGs and how we can actually reuse DAGs themselves.
- Monitoring in Airflow -->

- more plugins (hooks, operators, ...) by community
  - https://github.com/apache/airflow/tree/main/airflow/contrib
- create own plugins
  - airflow docs
    - https://airflow.apache.org/docs/apache-airflow/stable/howto/custom-operator.html
  - example custom operator
    - https://github.com/cgebbe/cd0031-automate-data-pipelines/blob/master/custom_operators/has_rows.py
  - usage of custom operator
    - https://github.com/cgebbe/cd0031-automate-data-pipelines/blob/master/lesson-5-production-data-pipelines/solution/l5_e1_custom_operators.py
- best practices
  - DAGs should be
    - atomic
    - maximize parallelism
    - make failure state obvious
  - task should...
    - do only one job
    - have clear boundaries between tasks
    - be easily parallelizable
    - minimize dependencies
  - example refactoring: split big task
    - original
      - https://github.com/cgebbe/cd0031-automate-data-pipelines/blob/master/lesson-5-production-data-pipelines/starter/l5_e2_refactor_dag.py
    - solution
      - https://github.com/cgebbe/cd0031-automate-data-pipelines/blob/master/lesson-5-production-data-pipelines/solution/l5_e2_refactor_dag.py
    - extracted tasks: three separated tasks + logging
      - find_riders
      - rides_per_bike
      - create_stations
      - log_result
- Airflow v1 to v2
  - major changes in v2
    - **TaskFlow API** = simpler way to define workflows (`@task`, `@dag` similar to Prefect)
    - better UI
    - improved performance (scheduler, database, ...)
    - native kubernetes support
    - **new testing framework**
    - improved docs and community support
  - to convert v1 to v2
    - Airflow1 instantiates the DAG directly with dag= DAG (...) whereas, with Airflow2, you'll use a decorator.
    - Airflow1 uses explicitly stated DAG names, but Airflow2 can infer DAG names from functions.
    - Airflow1 uses PythonOperator() in tasks, but in Airflow2, you'll use a regular Python function with the task decorator.
    - In Airflow2, you don't instantiate the DAG, so you don't have to pass the DAG.
- Monitoring
  - Airflow provides following features
    - SLAs (service-level agreement) = maximum completion time
    - Alerts upon DAG or task state changes to e.g. `PagerDuty` (Email, Phone, Slack, ...)
    - Metrics using `statsd`, which can be coupled using `Grafana` or `Prometheus`. Metrics can be coupled with alerts
    - Logging to local disk. Can be forwarded to `fluentd`

### Notes

- Udacity final example of building DAG
  - problem
    - https://github.com/cgebbe/cd0031-automate-data-pipelines/blob/master/lesson-5-production-data-pipelines/starter/l5_e4_build_full_dag.py
  - solution
    - https://github.com/cgebbe/cd0031-automate-data-pipelines/blob/master/lesson-5-production-data-pipelines/solution/l5_e4_build_full_dag.py
- links to different pipline tools
  - https://github.com/pditommaso/awesome-pipeline
