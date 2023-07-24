"""Utility functions for SQL querying."""
import pprint
from psycopg2.extras import RealDictCursor
import configparser
import psycopg2
from loguru import logger
import sys

logger.remove()
logger.add("log.log", level="INFO")
logger.add(sink=sys.stdout, level="INFO")


def read_config(config_path="dwh.cfg"):
    """Read config.

    :param config_path: path to config, defaults to "dwh.cfg"
    :return: config instance
    """
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def get_drop_query(table_name: str):
    """Generate DROP query for table..

    :param table_name: table name
    :return: string
    """
    return f"DROP TABLE IF EXISTS {table_name};"


def get_list_query(table_name: str, limit: int = 3):
    """Generate LIST query for table.

    :param table_name: table name
    :return: string
    """
    return f"SELECT * FROM {table_name} LIMIT {limit};"


def get_count_query(table_name: str):
    """Generate COUNT query for table..

    :param table_name: table name
    :return: string
    """
    return f"SELECT COUNT(*) FROM {table_name};"


class Connection:
    """Context manager to run SQL queries."""

    def __init__(self) -> None:
        """Initialize."""
        self.config = read_config()
        self.conn = None
        self.curr = None

    def __enter__(self):
        """Enter."""
        vals = list(self.config["CLUSTER"].values())
        self.conn = psycopg2.connect(
            "host={} dbname={} user={} password={} port={}".format(*vals)
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """Exit."""
        self.conn.close()

    def run(self, query: str):
        """Run query and log result."""
        query = query.strip()
        logger.info(query)
        assert query.endswith(";")

        self.cur.execute(query)
        try:
            rows = self.cur.fetchall()
            logger.info(pprint.pformat(rows))
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e):
                pass
            else:
                raise e
        self.conn.commit()
