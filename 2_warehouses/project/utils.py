from pprint import pprint
from psycopg2.extras import RealDictCursor
import configparser
import psycopg2


def read_config(config_path="dwh.cfg"):
    config = configparser.ConfigParser()
    config.read(config_path)
    return config


def get_drop_query(table_name: str):
    return f"DROP TABLE IF EXISTS {table_name};"


def get_list_query(table_name: str, limit: int = 3):
    return f"SELECT * FROM {table_name} LIMIT {limit};"


def get_count_query(table_name: str):
    return f"SELECT COUNT(*) FROM {table_name};"


class Connection:
    def __init__(self) -> None:
        self.config = read_config()
        self.conn = None
        self.curr = None

    def __enter__(self):
        vals = list(self.config["CLUSTER"].values())
        self.conn = psycopg2.connect(
            "host={} dbname={} user={} password={} port={}".format(*vals)
        )
        self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def run(self, query: str):
        query = query.strip()
        print(query)
        assert query.endswith(";")

        self.cur.execute(query)
        try:
            rows = self.cur.fetchall()
            pprint(rows)
        except psycopg2.ProgrammingError as e:
            if "no results to fetch" in str(e):
                pass
            else:
                raise e
        self.conn.commit()
