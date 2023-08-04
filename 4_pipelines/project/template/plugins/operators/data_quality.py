from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from typing import List
from dataclasses import dataclass, asdict


@dataclass
class CheckOperation:
    table: str
    query: str
    expected_result: str


class DataQualityOperator(BaseOperator):

    ui_color = "#89DA59"

    @apply_defaults
    def __init__(self, checks: List[CheckOperation], verbose=True, *args, **kwargs):
        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.checks = checks
        self.verbose = verbose

    def execute(self, context):
        del context
        hook = PostgresHook(postgres_conn_id="redshift")
        for c in self.checks:
            self.log.info(f"Checking {asdict(c)}")

            if self.verbose:
                self._run(hook, f"SELECT COUNT(*) FROM {c.table};")
                self._run(hook, f"SELECT * FROM {c.table} LIMIT 3;")

            records = self._run(hook, c.query)
            if records != c.expected_result:
                raise ValueError(f"Expected {records} to equal {c.expected_result}")

    def _run(self, hook: PostgresHook, query: str):
        self.log.info(f"Running query={query}")
        records = hook.get_records(query)
        self.log.info(f"records={records}")
        return records
