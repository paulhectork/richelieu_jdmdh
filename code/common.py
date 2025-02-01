"""
globally useful functions, constants and the Query class.
"""

from sqlalchemy import Engine, create_engine
import pandas as pd

import typing as t
import json
import os


def build_engine() -> Engine:
    """function to build an sqlalchemy engine for our db"""
    with open(os.path.join(CONFIG_DIR, "postgresql_conn.json"), mode="r") as fh:
        cred = json.load(fh)

    return create_engine(
        f"postgresql://{cred['username']}:{cred['password']}@{cred['uri']}/{cred['db']}",
        echo=False)



ROOT_DIR   = os.path.abspath("")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
ENGINE     = build_engine()
OUT_DIR    = os.path.join(ROOT_DIR, "out")

class Query():
    """class to hold all of our data related to queries"""
    sql: str                      # the querystring to extract data from the db
    basename: str            # root name of the output files (without extension or whatever)
    tablename: t.List[str]        # name of the tables used in `self.query`. if array has 1 item, it's the only table used in the query. if it has 2 tables, the 1st tablename is "table_from", the second is "table_to"
    df: t.Optional[pd.DataFrame]  # results of self.query in a dataframe. populated in other scripts

    def __init__(self, sql:str, basename:str, tablename:t.List[str]):
        self.sql = sql
        self.basename = basename
        self.tablename = tablename
        self.df = None  # populated in other scripts

