from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import List


class DataQualityOperator(BaseOperator):

    ui_color = "#89DA59"

    @apply_defaults
    def __init__(self, tables: List[str], *args, **kwargs):
        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.tables = tables

    def execute(self, context):
        del context
        hook = PostgresHook(postgres_conn_id="redshift")
        for table in self.tables:
            self.log.info(f"Checking table: {table}")

            # check row count. Answer is e.g. `[(6820,)]`
            records = hook.get_records(f"SELECT COUNT(*) FROM {table};")
            self.log.info(f"records={records}")
            if len(records) < 1 or len(records[0]) < 1 or records[0][0] < 1:
                raise ValueError(f"{table} contains 0 rows")

            # log first three rows
            records = hook.get_records(f"SELECT * FROM {table} LIMIT 3")
            self.log.info(f"First three records for table are: {records}")
