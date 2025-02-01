"""
study directed network of relationships from "theme|named_entity|place" to "iconography".
"""

import networkx as nx
import pandas as pd
import numpy as np

import typing as t
import os

from common import OUT_DIR, ENGINE, Query


# we use UUIDs instead of primary keys, because our graphs need node names to be unique.
# otherwise, we'd have duplicate values in `id_from` and `id_to`, so nodes would have duplicate names.
th_to_icn = """
            SELECT theme.id_uuid AS id_from,
                   theme.entry_name AS title_from,
                   iconography.id_uuid AS id_to
            FROM theme
            JOIN r_iconography_theme
            ON theme.id = r_iconography_theme.id_theme
            JOIN iconography
            ON r_iconography_theme.id_iconography = iconography.id
            ;
            """
pl_to_icn = """
            SELECT place.id_uuid AS id_from,
                   place.id_richelieu AS title_from,
                   iconography.id_uuid AS id_to
            FROM place
            JOIN r_iconography_place
            ON place.id = r_iconography_place.id_place
            JOIN iconography
            ON r_iconography_place.id_iconography = iconography.id
            ;
            """
ne_to_icn = """
            SELECT named_entity.id_uuid AS id_from,
                   named_entity.entry_name AS title_from,
                   iconography.id_uuid AS id_to
            FROM named_entity
            JOIN r_iconography_named_entity
            ON named_entity.id = r_iconography_named_entity.id_named_entity
            JOIN iconography
            ON r_iconography_named_entity.id_iconography = iconography.id
            ;
            """


queries = [ Query(th_to_icn, "th_to_icn", ["theme", "iconography"])
          , Query(pl_to_icn, "pl_to_icn", ["place", "iconography"])
          , Query(ne_to_icn, "ne_to_icn", ["named_entity", "iconography"])
          ]


def make_digraph(query_item) -> t.Tuple[Query, nx.DiGraph]:
    """
    create a DiGraph from a `Query`.

    Returns
        query_item (Query)
            augmented with a `df` that has 3 columns (id_from, title_from, id_to)
        G (nx.DiGraph)
            a directed acyclic graph documenting all relations from id_from to id_to.
            formally, nodes are `id_from` and `id_to` and edges all relations between id_from and id_to
    """
    query_item.df = pd.read_sql(query_item.sql, ENGINE)

    # make sure that values in id_from are not in id_to and vice versa.
    assert not any(id_uuid in query_item.df.id_to for id_uuid in query_item.df.id_from.drop_duplicates().to_list()) \
       and not any(id_uuid in query_item.df.id_from for id_uuid in query_item.df.id_to.drop_duplicates().to_list())

    nodes = query_item.df.id_from.drop_duplicates().to_list() + query_item.df.id_to.drop_duplicates().to_list()
    edges = list(query_item.df[["id_from", "id_to"]].itertuples(index=False, name=None))  # [(id_from, id_to)] : mapping of from and to nodes

    # our graphs are directed acyclic graphs of longest path 1.
    G = nx.DiGraph()  # https://networkx.org/documentation/stable/reference/classes/digraph.html#networkx.DiGraph
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)

    assert G.number_of_edges() == query_item.df.shape[0]
    return query_item, G


def analyze_digraph(query_item:Query, G:nx.DiGraph):
    """analyze the directed graph G produced in make_digraph"""
    out = {}  # output dictionnary holding statistics for the current query item

    # debug prints that may be useful
    # print("")
    # print(query_item.basename)
    # print("***********************************************")
    # print("is DAG:", nx.is_directed_acyclic_graph(G))
    # print("density: ", nx.density(G))
    # print("transitivity:", nx.transitivity(G))  # 0 since our longest path is of 1: no two "from" edges are connected.
    # print("longest path length: ", nx.dag_longest_path_length(G))  # always 1

    out["table_from"]          = query_item.tablename[0]
    out["table_to"]            = query_item.tablename[1]
    out["n_nodes"]             = nx.number_of_nodes(G)
    out["n_edges"]             = nx.number_of_edges(G)
    out["longest_path_length"] = nx.dag_longest_path_length(G)
    out["density"]             = nx.density(G)

    # extract minimum and maximum degrees in the graph
    # min/max degrees is the min/max
    deg = nx.degree(G)
    idx, val = zip(*deg)  # separate 1st element (id of the node) from second (degree of the node)
    s_deg = pd.Series(val, idx)
    s_deg = s_deg.loc[ s_deg.index.isin(query_item.df.id_from) ]  # discard all nodes that are in `df.id_to`, since we want to study the degree from qualifier to iconography only.
    out["deg_from_min"] = s_deg.min()
    out["deg_from_max"] = s_deg.max()
    out["deg_from_amplitude"] = s_deg.max() - s_deg.min()

    id_max = s_deg.loc[ s_deg.eq(s_deg.max()) ].index.to_series().to_list()  # array of "id_from" with the maximum centrality
    titles_max = query_item.df.loc[query_item.df.id_from.isin(id_max), "title_from"].drop_duplicates().to_list()
    out["deg_from_max_names"] = titles_max

    # measure outdegree centrality (centrality in an acyclic graph calculated by measuring all the edges that start from a given node)
    # we're only interested in the out-centrality of the `id_from` nodes: `id_to` nodes have an out-centrality of 0, since no nodes start from them and they only receive nodes.
    odc = nx.out_degree_centrality(G)
    s_odc = pd.Series(list(odc.values()), index=odc.keys())  # series of out_degree_centrality of all nodes in G
    s_odc = s_odc.loc[ s_odc.index.isin(query_item.df.id_from) ]  # remove all nodes that are found in df.id_to
    out["odc_from_max"]    = s_odc.max()
    out["odc_from_min"]    = s_odc.min()
    out["odc_from_mean"]   = s_odc.mean()
    out["odc_from_median"] = s_odc.median()

    # print("eigenvector centrality:", nx.eigenvector_centrality(G))  # computes the centrality for a node by adding the centrality of its predecessors. it takes into account if a node is a hub, but also how many hubs the node is connected to.
    # print("betweenness centrality:", nx.betweenness_centrality(G))  # centrality mesure based on shorted paths. since all our paths have the same length (1), this is useless.


    # print("\n".join(f"{k} : {v}" for k,v in out.items()))
    return out



def pipeline():
    """
    processing pipeline
    """
    results:t.List[t.Dict] = []
    for query_item in queries:
        query_item, G = make_digraph(query_item)
        out = analyze_digraph(query_item, G)
        results.append(out)
    df_results = pd.DataFrame.from_records(results)
    df_results.to_excel( os.path.join(OUT_DIR, "stats_network_result.xlsx")
                       , header=True, index=True, index_label="index")
    return


if __name__ == "__main__":
    pipeline()