import pandas as pd
from config import DATAFRAMES, JOHN_LABELS, BABBELNET_LABELS, YOVISTO_LABELS, CONFIDENCE_THRESHOLDS

def __compare_dataset_overlap(
    df1: pd.DataFrame, 
    df2: pd.DataFrame, 
    label: str, 
    print_result: bool = True, 
    confidence_column: str = None, 
    confidence_threshold: float = None
) -> pd.DataFrame:
    overlap_df = pd.merge(df1, df2, on='ili', how='inner')
    
    if confidence_column and confidence_threshold is not None:
        overlap_df[confidence_column] = overlap_df[confidence_column].astype(float)
        overlap_df = overlap_df[overlap_df[confidence_column] >= confidence_threshold]
    
    overlap_match_df = overlap_df[overlap_df['wikidata_x'] == overlap_df['wikidata_y']]
    overlap_mismatch_df = overlap_df[overlap_df['wikidata_x'] != overlap_df['wikidata_y']]
    
    result_data = {
        'Overlap': overlap_df['ili'].count(),
        'Match': overlap_match_df['ili'].count(),
        'Mismatch': overlap_mismatch_df['ili'].count(),
        'Success': round(overlap_match_df['ili'].count() / overlap_df['ili'].count(), 2) if overlap_df['ili'].count() > 0 else 0,
        'Label': label
    }
    result_pd = pd.DataFrame(result_data, index=[0])
    if print_result:
        print(f'\n{result_pd}\n')
    return result_pd

def __perform_analysis(base_df: pd.DataFrame, comparison_dfs: list, labels: list, print_result: bool = True) -> pd.DataFrame:
    results = []
    for comparison_df, label in zip(comparison_dfs, labels):
        results.append(__compare_dataset_overlap(base_df, comparison_df, label, False))
    merged_results = pd.concat(results, ignore_index=True)
    if print_result:
        print(f'\n{merged_results}\n')    
    return merged_results


def display_overview():
    # Analysis: John Wikidata
    print("\nJohn Mc. Wikidata Dataset Analysis\n")
    john_results = __perform_analysis(
        DATAFRAMES["oewn_wikidata_df"],
        [DATAFRAMES[df] for df in JOHN_LABELS['dataframes']],
        JOHN_LABELS['labels']
    )

    # Analysis: BabbelNet
    print("\nBabbelNet Dataset Analysis\n")
    babbelnet_results = __perform_analysis(
        DATAFRAMES["babel_net_df"],
        [DATAFRAMES[df] for df in BABBELNET_LABELS['dataframes']],
        BABBELNET_LABELS['labels']
    )

    # Analysis: Yovisto Kea and Spotlight with High Annotator Confidence Score
    print("\nYovisto Kea and Spotlight with High Annotator Confidence Score\n")
    john_spotlight_results = __compare_dataset_overlap(
        DATAFRAMES["oewn_wikidata_df"],
        DATAFRAMES["yovisto_wikidata_spotlight_df"],
        YOVISTO_LABELS['labels'][1],
        False,
        'score',
        CONFIDENCE_THRESHOLDS['spotlight']
    )

    john_kea_results = __compare_dataset_overlap(
        DATAFRAMES["oewn_wikidata_df"],
        DATAFRAMES["yovisto_wikidata_kea_df"],
        YOVISTO_LABELS['labels'][0],
        False,
        'score',
        CONFIDENCE_THRESHOLDS['kea']
    )

    john_combined_results = __compare_dataset_overlap(
        DATAFRAMES["oewn_wikidata_df"],
        DATAFRAMES["yovisto_wikidata_kea_and_spotlight_df"],
        YOVISTO_LABELS['labels'][2],
        False,
        'combined_score',
        CONFIDENCE_THRESHOLDS['combined']
    )

    babelnet_combined_results = __compare_dataset_overlap(
        DATAFRAMES["babel_net_df"],
        DATAFRAMES["yovisto_wikidata_kea_and_spotlight_df"],
        YOVISTO_LABELS['labels'][3],
        False,
        'combined_score',
        CONFIDENCE_THRESHOLDS['combined'] 
    )

    babelnet_spotlight_results = __compare_dataset_overlap(
        DATAFRAMES["babel_net_df"],
        DATAFRAMES["yovisto_wikidata_spotlight_df"],
        YOVISTO_LABELS['labels'][4],
        False,
        'score',
        CONFIDENCE_THRESHOLDS['spotlight']
    )

    babelnet_kea_results = __compare_dataset_overlap(
        DATAFRAMES["babel_net_df"],
        DATAFRAMES["yovisto_wikidata_kea_df"],
        YOVISTO_LABELS['labels'][5],
        False,
        'score',
        CONFIDENCE_THRESHOLDS['kea']
    )

    # Combine filtered results
    filtered_yovisto_results = pd.concat(
        [
            john_spotlight_results,
            john_kea_results,
            john_combined_results,        
            babelnet_spotlight_results,
            babelnet_kea_results,
            babelnet_combined_results
        ],
        ignore_index=True
    )
    print(f'\n{filtered_yovisto_results}\n')

# The above code is a standalone script that performs analysis on different datasets, comparing overlaps and matches.
# It uses pandas for data manipulation and sqlite3 for database connections.
# The script defines functions to compare datasets, perform analysis, and display results.
# The display_overview function orchestrates the analysis by calling the comparison functions with appropriate datasets and labels.
# The results are printed to the console, providing insights into the overlaps and matches between different datasets.
display_overview()