import pandas as pd
import sqlite3
from queries import BABBELNET_QUERY, YOVISTO_COMBINED_QUERY

# Load data
conn = sqlite3.connect("wordnet_wikidata_mapping.db")
DATAFRAMES = {
    "yovisto_wikidata_kea_and_spotlight_df": pd.read_sql(YOVISTO_COMBINED_QUERY, conn),
    "yovisto_wikidata_kea_df": pd.read_sql("select * from yovisto_wikidata_kea_annotator", conn),
    "yovisto_wikidata_spotlight_df": pd.read_sql("select * from yovisto_wikidata_spotlight_annotator", conn),
    "oewn_wikidata_df": pd.read_sql("select * from oewn_wikidata", conn),
    "gf_wikidata_30428_df": pd.read_sql("select * from gf_wikidata", conn),
    "babel_net_df": pd.read_sql(BABBELNET_QUERY, conn)
}
conn.close()

JOHN_LABELS = {
    "dataframes": [
        "yovisto_wikidata_spotlight_df",
        "yovisto_wikidata_kea_df",
        "yovisto_wikidata_kea_and_spotlight_df",
        "gf_wikidata_30428_df"
    ],
    "labels": [
        "oewn_wikidata and yovisto_wikidata_spotlight",
        "oewn_wikidata and yovisto_wikidata_kea",
        "oewn_wikidata and yovisto_wikidata_intersection",
        "oewn_wikidata and gf_wikidata"
    ]
}

BABBELNET_LABELS = {
    "dataframes": [
        "oewn_wikidata_df",
        "yovisto_wikidata_spotlight_df",
        "yovisto_wikidata_kea_df",
        "yovisto_wikidata_kea_and_spotlight_df",
        "gf_wikidata_30428_df"
    ],
    "labels": [
        "babbelnet and oewn_wikidata",
        "babbelnet and yovisto_wikidata_spotlight",
        "babbelnet and yovisto_wikidata_kea",
        "babbelnet and yovisto_wikidata_intersection",
        "babbelnet and gf_wikidata"
    ]
}

YOVISTO_LABELS = {
    "dataframes": [
        "yovisto_wikidata_kea_df",
        "yovisto_wikidata_spotlight_df",
        "yovisto_wikidata_kea_and_spotlight_df"
    ],
    "labels": [
        "yovisto_wikidata_kea and oewn_wikidata",
        "yovisto_wikidata_spotlight and oewn_wikidata",
        "yovisto_wikidata_intersection and oewn_wikidata",
        "yovisto_wikidata_intersection and babelnet",
        "yovisto_wikidata_spotlight and babelnet",
        "yovisto_wikidata_kea and babelnet"
    ]
}

CONFIDENCE_THRESHOLDS = {
    "kea": 0.67,
    "spotlight": 0.95,
    "combined": 1.6
}
