# import argparse
# import json
# import os
# import pathlib
# import sys
from pathlib import Path

import pandas as pd
from taxaplease.taxaplease import TaxaPlease

__version__ = "0.1.1"


ranks = ["Species", "Genus", "Family", "Order", "Kingdom", "Phylum"]
Families = ["Archaea", "Bacteria", "Eukaryote", "Fungi", "Phage", "Virus"]


# TODO. use TaxaPlease database to create the ranks and family lists. Therefore stay consistent with any updates


def get_ranks():
    pass


def get_families():
    pass


def load_report(report_path: str) -> pd.DataFrame:
    columns = ["percent_coverage", "no_reads_covered", "no_reads_assigned", "rank", "taxid", "name"]
    df = pd.read_csv(Path(report_path), sep="\t", names=columns)
    return df


def load_results(results_path: str) -> pd.DataFrame:
    columns = ["isClassified", "header", "taxid", "length", "kmer_map"]
    df = pd.read_csv(Path(results_path), sep="\t", names=columns)
    return df


def search_rank(results_df: pd.DataFrame, rank: list) -> pd.DataFrame:
    pass


def which_family(df: pd.DataFrame, database_path: str, Family: list, choice: str) -> pd.DataFrame:
    """initiate TaxaPlease and use isVirus function (->bool) to determine if taxids found are listed as viruses in NCBI database."""
    taxaPlease = TaxaPlease(database=database_path)
    func = {
        Family: getattr(taxaPlease, f"is{choice.capitalize()}")
        for Family in Families
        }
    df = df.assign(**{f"is_{choice}": df["taxid"].apply(lambda x: func[choice](x))})
    return df


def which_family2(df: pd.DataFrame, choice: str, tp_func) -> pd.DataFrame:
    df = df.assign(**{f"is_{choice}": df["taxid"].apply(tp_func)})
    return df


def run_detection(sample_id: str, report_path: str, database_path: str, family:str, tp_func):
    print("running")
    df = load_report(report_path=report_path)
    
    df1 = which_family(df=df,
                      database_path=database_path,
                      Family=Families,
                      choice=family)
    print(df1)
    df2 = which_family2(df=df,
                        choice=family,
                        tp_func=tp_func)
    print(df2)