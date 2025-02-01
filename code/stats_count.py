"""
compute general statistics on "count" columns (counting number of relations from tableA to tableB)
"""
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os

import typing as t

from common import ENGINE, OUT_DIR, Query

# define a GUI bacckend to show the plots
matplotlib.use('TkAgg')

if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)


# ne categories mapped to number of ne's in this category
ne_category_to_ne_count = """
SELECT
    named_entity.category,
    COUNT(named_entity.id_uuid) AS count_result
FROM named_entity
GROUP BY named_entity.category
ORDER BY count_result DESC;
"""

# theme categories mapped to number of themes in this category
theme_category_to_theme_count ="""
SELECT
    theme.category,
    COUNT(theme.id_uuid) AS count_result
FROM theme
GROUP BY theme.category
ORDER BY count_result DESC;
"""

# theme mapped to number of iconographies for this theme
theme_to_iconography_count ="""
SELECT
    theme.id,
    COUNT(r_iconography_theme.id) AS "count_result"
FROM theme
JOIN r_iconography_theme ON r_iconography_theme.id_theme = theme.id
GROUP BY theme.id, theme.entry_name, r_iconography_theme.id_theme
ORDER BY count_result DESC;
"""

# ne mapped to number of iconographies for this named_entity
ne_to_iconography_count = """
SELECT
    named_entity.id,
    COUNT(r_iconography_named_entity.id) AS "count_result"
FROM named_entity
JOIN r_iconography_named_entity
    ON r_iconography_named_entity.id_named_entity = named_entity.id
GROUP BY
    named_entity.id,
    r_iconography_named_entity.id_named_entity
ORDER BY count_result DESC;
"""

# places mapped to number of iconographies
place_to_iconography_count = """
SELECT
    place.id,
    COUNT(r_iconography_place.id) AS "count_result"
FROM place
JOIN r_iconography_place ON r_iconography_place.id_place = place.id
GROUP BY place.id, place.id_richelieu, r_iconography_place.id_place
ORDER BY count_result DESC;
"""

# iconography mapped to number of places
iconography_to_place_count = """
SELECT
    iconography.id,
    COUNT(r_iconography_place.id) AS count_result
FROM iconography
JOIN r_iconography_place ON iconography.id = r_iconography_place.id_iconography
GROUP BY iconography.id
ORDER BY count_result DESC;
"""

# iconography mapped to number of named entities
iconography_to_ne_count = """
SELECT
    iconography.id,
    COUNT(r_iconography_named_entity.id) AS count_result
FROM iconography
JOIN r_iconography_named_entity
    ON iconography.id = r_iconography_named_entity.id_iconography
GROUP BY iconography.id
ORDER BY count_result DESC;
"""

# iconography mapped to number of themes
iconography_to_theme_count = """
SELECT
    iconography.id,
    COUNT(r_iconography_theme.id) AS count_result
FROM iconography
JOIN r_iconography_theme
    ON iconography.id = r_iconography_theme.id_iconography
GROUP BY iconography.id
ORDER BY count_result DESC;
"""


queries_data: t.List[Query] = (
    [ Query( ne_category_to_ne_count, "ne_category_to_ne_count", [ "named_entity", "named_entity" ] )
    , Query( theme_category_to_theme_count, "theme_category_to_theme_count", [ "theme", "theme" ] )
    , Query( theme_to_iconography_count, "theme_to_iconography_count", [ "theme", "iconography" ] )
    , Query( ne_to_iconography_count, "ne_to_iconography_count", [ "named_entity", "iconography" ] )
    , Query( place_to_iconography_count, "place_to_iconography_count", [ "place", "iconography" ] )
    , Query( iconography_to_place_count, "iconography_to_place_count", [ "iconography", "place" ] )
    , Query( iconography_to_ne_count, "iconography_to_ne_count", [ "iconography", "named_entity" ] )
    , Query( iconography_to_theme_count, "iconography_to_theme_count", [ "iconography", "theme" ] )
    ])


def get_entry_name(tablename:str) -> pd.DataFrame:
    """
    returns
        a dataframe with 2 columns:
        id_        (int): tablename.id)
        entry_name (str): human readable value for a row
    """
    if tablename == "iconography":
        sql = """
            SELECT iconography.id AS id_, title.entry_name AS entry_name
            FROM iconography
            JOIN title ON title.id_iconography = iconography.id;"""
    elif tablename == "place":
        sql = """
            SELECT place.id AS id_, place.id_richelieu AS entry_name
            FROM place;"""
    elif tablename == "named_entity":
        sql = """
            SELECT named_entity.id AS id_, named_entity.entry_name AS entry_name
            FROM named_entity;"""
    elif tablename == "theme":
        sql = """
            SELECT theme.id AS id_, theme.entry_name AS entry_name
            FROM theme;"""
    else:
        raise ValueError("expected one of ['iconogrpahy', 'place', 'named_entity', 'theme']")

    df = pd.read_sql(sql, ENGINE)

    if tablename == "iconography":
        df = df.drop_duplicates(subset="id_", keep="first")
    return df


def sql_to_df(query_item:Query) -> Query:
    """
    prepare a dataframe from running SQL queries
    and assign the result to `query_item.df`.

    df will have the columns:
        - id_           (int|str): primary key of query_item.tablename
        - entry_name    (str)    : human-readable value for the row
        - count_results (int)    : result of the count function in `query_item.sql`

    params
        query_item: the object containing SQL query and all extra data.
    returns
        query_item augmented with a `df` attribute.
    """
    df = pd.read_sql(query_item.sql, ENGINE)
    df.columns = ["id_", "count_result"]  # rename columns to homogenize output

    # extract a human-readable "title" for each row of the df
    if query_item.basename in ["ne_category_to_ne_count", "theme_category_to_theme_count"]:
        df["entry_name"] = df.id_
    else:
        df_entry_name = get_entry_name(query_item.tablename[0])
        df = df.merge(df_entry_name, how="left", on="id_")

    df = df[["id_", "entry_name", "count_result"]]

    query_item.df = df
    return query_item


def stats_for_query_item(query_item:Query) -> Query:
    """make statistics"""
    out = { "title": query_item.basename, "min_val": None, "max_val": None, "amplitude": None, "median": None, "mean": None, "quantiles": None, "counts": None }

    out["min_val"]   = query_item.df.count_result.min()
    out["max_val"]   = query_item.df.count_result.max()
    out["mean"]      = query_item.df.count_result.mean()
    out["median"]    = query_item.df.count_result.median()
    out["amplitude"] = out["max_val"]-out["min_val"]

    # quantiles to study the distribution of "nb_relations"
    s_quantiles = query_item.df.count_result.quantile(q=[0, 0.25, 0.5, 0.75, 1])  # s_ = series
    out["quantiles"] = s_quantiles.to_list()
    # make df_quantiles sexier if we want to save it to its own file.
    df_quantiles = (s_quantiles.reset_index(drop=False)
                               .rename(columns={"index": "quantile", "count_result": "nb_relations"}))

    # mapping of all distinct numbers of relations from tableA to tableB to the number of rows with that number of relations...
    # reads: 1025 rows (nb_rows) of tableA have 3 relations (nb_relations) to tableB.
    # nb_relations = number of relations for a row
    # nb_rows = number of rows with a certain number of relationships
    df_counts    = (pd.DataFrame( query_item.df.value_counts(subset=["count_result"]) )
                   .reset_index(drop=False)
                   .rename(columns={"count": "row_count", "count_result": "nb_relations"})
                   .sort_values(by="nb_relations"))
    out["counts"] = df_counts.to_dict("records")

    # write some plots
    kind = "scatter" if query_item.basename == "theme_to_iconography_count" else "line"
    name = f"{query_item.basename}_counts"
    plot = df_counts.plot( x="nb_relations", y="row_count"
                         , title=name
                         , xlabel=f"number of relations from {query_item.tablename[0]} to {query_item.tablename[1]}"
                         , ylabel="row count"
                         , kind=kind)
    plt.savefig(os.path.join(OUT_DIR, f"{name}.png"))
    plt.close()

    # # make a second plot removing high values
    # if query_item.basename == "theme_to_iconography_count":
    #     df_counts = df_counts.loc[df_counts.nb_relations < 750]
    #     df_counts.plot(x="nb_relations", y="nb_rows", kind=kind,
    #                    title=f"{query_item.basename}_tight")

    return out


def pipeline():
    """processing pipeline"""

    # run query and extract statistics
    results = []
    for query_item in queries_data:
        query_item = sql_to_df(query_item)
        results.append( stats_for_query_item(query_item) )
    df_results = pd.DataFrame.from_records(results)

    df_results.to_excel( os.path.join(OUT_DIR, "stats_count_result.xlsx")
                       , header=True, index=True, index_label="index")

    return


if __name__ == "__main__":
    pipeline()

