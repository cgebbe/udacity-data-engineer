from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator


import operators
import helpers
# import operators
# import helpers

# try:
#     # `helpers` is in the plugin directory
#     import helpers  #  import SqlQueries
#     from airflow import operators
# except ModuleNotFoundError:
#     plugin_dirpath = Path(__file__).resolve().parents[1] / "plugins"
#     assert plugin_dirpath.exists(), plugin_dirpath
#     print()
#     site.addsitedir(plugin_dirpath)
#     import operators
#     import helpers


# AWS_KEY = os.environ.get('AWS_KEY')
# AWS_SECRET = os.environ.get('AWS_SECRET')


dag = DAG(
    "udac_example_dag",
    default_args={
        "owner": "udacity",
        "start_date": datetime(2019, 1, 12),
        "depends_on_past": False,
        "retries": 3,
        "retry_delay": timedelta(minutes=5),
        "catchup": False,
        "email_on_retry": False,
    },
    description="Load and transform data in Redshift with Airflow",
    # is scheduled every hour. Why is that?!
    schedule_interval="0 * * * *",
)

start_operator = DummyOperator(task_id="Begin_execution", dag=dag)

# STAGE

stage_events_to_redshift = operators.StageToRedshiftOperator(
    task_id="Stage_events", dag=dag
)
stage_songs_to_redshift = operators.StageToRedshiftOperator(
    task_id="Stage_songs", dag=dag
)

start_operator << stage_events_to_redshift
start_operator << stage_songs_to_redshift

# LOAD SONGPLAYS

load_songplays_table = operators.LoadFactOperator(
    task_id="Load_songplays_fact_table", dag=dag
)

stage_events_to_redshift << load_songplays_table
stage_songs_to_redshift << load_songplays_table

# LOAD DIM TABLES 

load_user_dimension_table = operators.LoadDimensionOperator(
    task_id="Load_user_dim_table", dag=dag
)
load_song_dimension_table = operators.LoadDimensionOperator(
    task_id="Load_song_dim_table", dag=dag
)
load_artist_dimension_table = operators.LoadDimensionOperator(
    task_id="Load_artist_dim_table", dag=dag
)
load_time_dimension_table = operators.LoadDimensionOperator(
    task_id="Load_time_dim_table", dag=dag
)

load_songplays_table << load_user_dimension_table
load_songplays_table << load_song_dimension_table
load_songplays_table << load_artist_dimension_table
load_songplays_table << load_time_dimension_table

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