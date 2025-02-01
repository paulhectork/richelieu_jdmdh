"""
sql queries and functions to generate sql queries
"""

import pandas as pd
import typing as t

from common import Query


########################################################

# generates an sql query to fetch column 'colname'
# from all rows in 'tablename' with an "table.id" in "id_array"
get_extra_column = lambda tablename, colname, id_array: (
    f"""
    SELECT {tablename}.{colname}
    FROM {tablename}
    WHERE {tablename}.id IN {id_array}
    """)
