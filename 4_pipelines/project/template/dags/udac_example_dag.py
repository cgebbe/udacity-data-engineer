from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.decorators import dag

from airflow.operators.postgres_operator import PostgresOperator

try:
    from ..plugins import operators
    from ..plugins import helpers
except:
    import operators
    import helpers


import pendulum
from typing import List
from pathlib import Path


def _filter_empty_items(lst):
    return [x for x in lst if x]


def _create_tables_op():
    drop_queries = []
    for t in [
        "artists",
        "songplays",
        "songs",
        "staging_events",
        "staging_songs",
        "time",
        "users",
    ]:
        drop_queries.append(f" DROP TABLE IF EXISTS {t};")

    filepath = Path(__file__).parent / "new/create_tables.sql"
    assert filepath.exists(), filepath
    create_queries = [
        s.replace("\n", "").replace("\t", "") for s in filepath.read_text().split(";")
    ]

    all_queries = _filter_empty_items(drop_queries + create_queries)

    return PostgresOperator(
        task_id="create_tables",
        sql=all_queries,
        postgres_conn_id="redshift",
        autocommit=True,
    )


def _get_default_args(is_submission: bool) -> dict:
    dct = {
        "owner": "udacity",
        # If datetime(2019,1,12) it doesn't start?! Maybe also due to schedule_interval
        "start_date": datetime(2019, 1, 12) if is_submission else pendulum.now(),
        "depends_on_past": False,
        "retries": 3 if is_submission else 1,
        "retry_delay": timedelta(minutes=5),
        "catchup": False,
        "email_on_retry": False,
    }
    if is_submission:
        # If schedule interval is set seems to only start every hour?!
        dct["schedule_interval"] == "0 * * * *"
    return dct


@dag(
    "udacity",
    default_args=_get_default_args(is_submission=False),
    description="Load and transform data in Redshift with Airflow",
)
def pipe():
    start_operator = DummyOperator(task_id="Begin_execution")

    # create tables
    create_tables = _create_tables_op()
    start_operator >> create_tables

    # stage tables
    stage_songs_to_redshift = operators.StageToRedshiftOperator(
        task_id="stage_songs",
        redshift_table_name="staging_songs",
        s3_path="s3://udacity-dataengineer-pipeline-project-s3/song_data/A/A/A/",
        json_method="auto",
    )
    stage_events_to_redshift = operators.StageToRedshiftOperator(
        task_id="stage_events",
        redshift_table_name="staging_events",
        s3_path="s3://udacity-dataengineer-pipeline-project-s3/log_data",
        json_method="s3://udacity-dataengineer-pipeline-project-s3/log_json_path.json",
    )
    create_tables >> stage_events_to_redshift
    create_tables >> stage_songs_to_redshift

    # insert fact table
    load_songplays_table = operators.LoadFactOperator(
        task_id="Load_songplays_fact_table",
        query=helpers.SqlQueries.songplay_table_insert,
    )
    stage_events_to_redshift >> load_songplays_table
    stage_songs_to_redshift >> load_songplays_table

    # insert dim tables
    load_user_dimension_table = operators.LoadDimensionOperator(
        task_id="Load_user_dim_table",
        query=helpers.SqlQueries.user_table_insert,
    )
    load_song_dimension_table = operators.LoadDimensionOperator(
        task_id="Load_song_dim_table",
        query=helpers.SqlQueries.song_table_insert,
    )
    load_artist_dimension_table = operators.LoadDimensionOperator(
        task_id="Load_artist_dim_table",
        query=helpers.SqlQueries.artist_table_insert,
    )
    load_time_dimension_table = operators.LoadDimensionOperator(
        task_id="Load_time_dim_table",
        query=helpers.SqlQueries.time_table_insert,
    )
    load_songplays_table >> load_user_dimension_table
    load_songplays_table >> load_song_dimension_table
    load_songplays_table >> load_artist_dimension_table
    load_songplays_table >> load_time_dimension_table


pipe_dag = pipe()


if 0:

    # LOAD DIM TABLES

    # QUALITY

    run_quality_checks = operators.DataQualityOperator(
        task_id="Run_data_quality_checks", dag=dag
    )

    load_user_dimension_table << run_quality_checks
    load_song_dimension_table << run_quality_checks
    load_artist_dimension_table << run_quality_checks
    load_time_dimension_table << run_quality_checks

    # END

    end_operator = DummyOperator(task_id="Stop_execution", dag=dag)

    run_quality_checks << end_operator
