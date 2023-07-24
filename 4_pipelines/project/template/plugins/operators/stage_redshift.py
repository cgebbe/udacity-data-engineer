from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'

    @apply_defaults
    def __init__(self,
                 # Define your operators params (with defaults) here
                 # Example:
                 # redshift_conn_id=your-connection-name
                 s3_path,
                 redshift_table_name,
                 *args,
                 **kwargs,
                 ):

        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.s3_path = s3_path
        self.redshift_table_name = redshift_table_name
        # Map params here
        # Example:
        # self.conn_id = conn_id

    def execute(self, context):
        self.log.info('StageToRedshiftOperator not implemented yet')





