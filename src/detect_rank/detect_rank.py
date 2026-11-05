import json
from pathlib import Path

import pandas as pd
from taxaplease.taxaplease import TaxaPlease

__version__ = "0.1.1"


ranks = ["Species", "Genus", "Family", "Order", "Kingdom", "Phylum"]
#Families = ["Archaea", "Bacteria", "Eukaryote", "Fungi", "Phage", "Virus"]


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


def search_rank(df: pd.DataFrame, rank: ranks) -> pd.DataFrame:
    df_rank = df[df["rank"].eq(rank[0])]
    return df_rank


# def which_family(df: pd.DataFrame, database_path: str, Family: list, choice: str) -> pd.DataFrame:
#     """initiate TaxaPlease and use isVirus function (->bool) to determine if taxids found are listed as viruses in NCBI database."""
#     taxaPlease = TaxaPlease(database=database_path)
#     func = {
#         Family: getattr(taxaPlease, f"is{choice.capitalize()}")
#         for Family in Families
#         }
#     df = df.assign(**{f"is_{choice}": df["taxid"].apply(lambda x: func[choice](x))})
#     return df


def which_family(df: pd.DataFrame, choice: str, tp_func) -> pd.DataFrame:
    df = df.assign(**{f"is_{choice}": df["taxid"].apply(tp_func)})
    return df


def check_presence(df:pd.DataFrame):
    """check to see if there are any return viral/fungi/etc. reads based on the length of passed DataFrame."""
    if len(df) == 0:
        return False
    elif len(df) > 0:
        return True

def create_json(sample_id:str, df_genus: pd.DataFrame, df_species: pd.DataFrame, outdir: str): 
    json_setup = {
        "climb_id": sample_id,
        "virus_presence_genus": check_presence(df_genus),
        "virus_presence_species": check_presence(df_species),
        "genus": ', '.join(df_genus["name"].str.strip()),
        "genus_taxids": ', '.join(df_genus["taxid"].astype(str)),
        "species": ', '.join(df_species["name"].str.strip()),
        "species_taxids": ', '.join(df_species["taxid"].astype(str)),
    }
    outfile = Path(f"{outdir}/{id}_data.json")
    outfile.write_text(json.dumps(json_setup), encoding="utf-8")


def run_detection(sample_id: str, report_path: str, database_path: str, family:str, outdir:str, tp_func):
    print("running")
    df = load_report(report_path=report_path)
    
    # df1 = which_family(df=df,
    #                   database_path=database_path,
    #                   Family=Families,
    #                   choice=family)
    # print(df1)
    df_genus_level_detection = search_rank(df=df,
                                           rank="Genus")
    
    df_genus_level_detection = which_family(df=df_genus_level_detection,
                                            choice=family,
                                            tp_func=tp_func)
    
    df_species_level_detection = search_rank(df=df,
                                             rank="Species")
    
    df_species_level_detection = which_family(df=df_species_level_detection,
                                              choice=family,
                                              tp_func=tp_func)
    
    print(df_genus_level_detection)
    print(df_species_level_detection)
    create_json(sample_id=sample_id,
                df_genus= df_genus_level_detection,
                df_species=df_species_level_detection,
                outdir=outdir)