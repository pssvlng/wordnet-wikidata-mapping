import pandas as pd
import sqlite3
from queries import BABBELNET_QUERY

# Load data
conn = sqlite3.connect("wordnet_wikidata_mapping.db")
DATAFRAMES = {
    "yovisto_wikidata_kea_and_spotlight_df": pd.read_sql("select * from yovisto_wikidata_kea_and_spotlight_annotator", conn),
    "yovisto_wikidata_kea_df": pd.read_sql("select * from yovisto_wikidata_kea_annotator", conn),
    "yovisto_wikidata_spotlight_df": pd.read_sql("select * from yovisto_wikidata_spotlight_annotator", conn),
    "john_wikidata_df": pd.read_sql("select * from john_wikidata", conn),
    "krasimir_wikidata_30428_df": pd.read_sql("select * from krasimir_wikidata", conn),
    "babel_net_df": pd.read_sql(BABBELNET_QUERY, conn)
}
conn.close()

JOHN_LABELS = {
    "dataframes": [
        "yovisto_wikidata_spotlight_df",
        "yovisto_wikidata_kea_df",
        "yovisto_wikidata_kea_and_spotlight_df",
        "krasimir_wikidata_30428_df"
    ],
    "labels": [
        "john_wikidata and yovisto_wikidata_spotlight",
        "john_wikidata and yovisto_wikidata_kea",
        "john_wikidata and yovisto_wikidata (combined)",
        "john_wikidata and krasimir_wikidata"
    ]
}

BABBELNET_LABELS = {
    "dataframes": [
        "john_wikidata_df",
        "yovisto_wikidata_spotlight_df",
        "yovisto_wikidata_kea_df",
        "yovisto_wikidata_kea_and_spotlight_df",
        "krasimir_wikidata_30428_df"
    ],
    "labels": [
        "babbelnet and john_wikidata",
        "babbelnet and yovisto_wikidata_spotlight",
        "babbelnet and yovisto_wikidata_kea",
        "babbelnet and yovisto_wikidata (combined)",
        "babbelnet and krasimir_wikidata"
    ]
}

YOVISTO_LABELS = {
    "dataframes": [
        "yovisto_wikidata_kea_df",
        "yovisto_wikidata_spotlight_df",
        "yovisto_wikidata_kea_and_spotlight_df"
    ],
    "labels": [
        "yovisto_wikidata_kea and john_wikidata",
        "yovisto_wikidata_spotlight and john_wikidata",
        "yovisto_wikidata (combined) and john_wikidata",
        "yovisto_wikidata (combined) and babelnet",
        "yovisto_wikidata_spotlight and babelnet",
        "yovisto_wikidata_kea and babelnet"
    ]
}

CONFIDENCE_THRESHOLDS = {
    "kea": 0.67,
    "spotlight": 0.95,
    "combined": 1.6
}
