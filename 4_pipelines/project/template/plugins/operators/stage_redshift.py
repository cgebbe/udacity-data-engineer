from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import inspect


def _clean_query(q: str):
    return inspect.cleandoc(q).replace("\n ", " ")


class StageToRedshiftOperator(BaseOperator):
    ui_color = "#358140"

    @apply_defaults
    def __init__(
        self,
        # Define your operators params (with defaults) here
        # Example:
        # redshift_conn_id=your-connection-name
        s3_path: str,
        redshift_table_name: str,
        json_method: str,
        *args,
        **kwargs,
    ):
        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)

        self.s3_path = s3_path
        self.redshift_table_name = redshift_table_name
        self.json_method = json_method

    def execute(self, context):
        del context

        query = f"""
        COPY {self.redshift_table_name}
        FROM '{self.s3_path}'
        IAM_ROLE 'arn:aws:iam::561130499334:role/my-redshift-service-role'
        JSON '{self.json_method}'
        STATUPDATE ON
        MAXERROR 1
        COMPUPDATE OFF;
        """

        self.log.info(f"Running query: {query}")
        hook = PostgresHook(postgres_conn_id="redshift")
        hook.run(
            sql=_clean_query(query),
            autocommit=True,
        )
