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
Family = ["Archaea", "Bacteria", "Eukaryote", "Fungi", "Phage", "Virus"]


def load_report(report_path: str) -> pd.DataFrame:
    pass


def load_results(results_path: str) -> pd.DataFrame:
    pass


def search_rank(results_df: pd.DataFrame, rank: list) -> pd.DataFrame:
    pass


def which_family(df: pd.DataFrame, database_path: str, Family: list) -> pd.DataFrame:
    pass


def run_detection():
    print("running")
    pass