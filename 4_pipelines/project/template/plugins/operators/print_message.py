from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class PrintMessageOperator(BaseOperator):
    """
    Custom operator that prints a message to the logs.
    """

    @apply_defaults
    def __init__(self, message, *args, **kwargs):
        super(PrintMessageOperator, self).__init__(*args, **kwargs)
        self.message = message

    def execute(self, context):
        self.log.info(self.message)
