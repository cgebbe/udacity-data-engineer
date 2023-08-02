from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import inspect


def _clean_query(q: str) -> str:
    return inspect.cleandoc(q).replace("\n ", " ")


class LoadDimensionOperator(BaseOperator):

    ui_color = "#80BD9E"

    @apply_defaults
    def __init__(self, query: str, overwrite: bool = True, *args, **kwargs):
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.query = query
        self.overwrite = overwrite

    def execute(self, context):
        queries = [self.query]
        self.log.info(f"self.query={self.query}")

        if self.overwrite:
            q = _clean_query(self.query)
            self.log.info(f"cleaned query={q}")
            assert q.startswith("INSERT INTO")
            table_name = q.split(" ")[2]
            queries.insert(0, f"TRUNCATE {table_name};")

        hook = PostgresHook(postgres_conn_id="redshift")
        hook.run(
            sql=queries,
            autocommit=True,
        )
