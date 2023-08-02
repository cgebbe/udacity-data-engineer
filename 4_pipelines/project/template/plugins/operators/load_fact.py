from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults


class LoadFactOperator(BaseOperator):

    ui_color = "#F98866"

    @apply_defaults
    def __init__(self, query: str, *args, **kwargs):
        super(LoadFactOperator, self).__init__(*args, **kwargs)
        self.query = query

    def execute(self, context):
        self.log.info(f"self.query={self.query}")
        hook = PostgresHook(postgres_conn_id="redshift")
        hook.run(
            sql=self.query,
            autocommit=True,
        )
