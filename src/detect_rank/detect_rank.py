import json
import sys
from pathlib import Path

import pandas as pd

__version__ = "0.1.1"


ranks = ["Species", "Genus", "Family", "Order", "Kingdom", "Phylum"]
# Families = ["Archaea", "Bacteria", "Eukaryote", "Fungi", "Phage", "Virus"]


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


def which_family(df: pd.DataFrame, choice: str, tp_func) -> pd.DataFrame:
    col = f"is_{choice}"
    df = df.assign(**{col: df["taxid"].apply(tp_func)})
    df = df[df[col].astype(str).str.lower().eq("true")]
    return df


def check_presence(df:pd.DataFrame):
    """check to see if there are any return viral/fungi/etc. reads based on the length of passed DataFrame."""
    if len(df) == 0:
        return False
    elif len(df) > 0:
        return True


def create_json(sample_id: str, rank: str, df_genus: pd.DataFrame, df_species: pd.DataFrame, out_dir: str): 
    json_setup = {
        "climb_id": sample_id,
        f"{rank.lower()}_presence_genus": check_presence(df_genus),
        f"{rank.lower()}_presence_species": check_presence(df_species),
        "genus": ', '.join(df_genus["name"].str.strip()),
        "genus_taxids": ', '.join(df_genus["taxid"].astype(str)),
        "species": ', '.join(df_species["name"].str.strip()),
        "species_taxids": ', '.join(df_species["taxid"].astype(str)),
    }
    outfile = Path(f"{out_dir}/{sample_id}_data.json")
    outfile.write_text(json.dumps(json_setup), encoding="utf-8")


def run_detection(sample_id: str, report_path: str, database_path: str, family:str, out_dir:str, tp_func):
    print("running")
    df = load_report(report_path=report_path)
    
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

    create_json(sample_id=sample_id,
                rank=family,
                df_genus= df_genus_level_detection,
                df_species=df_species_level_detection,
                out_dir=out_dir)
    
    
#### 

"""Script to create an aggregated count from lineage data."""
### taken from epi2ome/wf-metagenomics under the conditions of their license https://github.com/epi2me-labs/wf-metagenomics/blob/master/LICENSE and modified for this use case. copied from scylla https://github.com/artic-network/scylla/blob/2bbc52aa36811d8ab36918e4eda2f83b17d62a13/bin/aggregate_lineages_bracken.py 

UNCLASSIFIED = "Unclassified"
UNKNOWN = "Unknown"

RANKS = [
    "superkingdom",
    "clade",
    "kingdom",
    "phylum",
    "subphylum",
    "class",
    "order",
    "family",
    "genus",
    "species",
    "subspecies",
    "serotype",
]


def update_or_create_unclassified(entries, unclassified_count):
    """Handle unclassified entries."""
    entries[UNCLASSIFIED] = {
        "taxid": 0,
        "rank": RANKS[0],
        "count": int(unclassified_count),
        "children": {
            UNKNOWN: {
                "taxid": 0,
                "rank": "species",
                "count": int(unclassified_count),
                "children": {},
            }
        },
    }
    return entries


def update_or_create_count(entry, entries, bracken_counts):
    """Increment lineage counts given entries."""
    taxid, lineage, ranks = entry.rstrip().split("\t")
    lineage_split = lineage.split(";")
    ranks_split = ranks.split(";")
    count = int(bracken_counts[taxid])

    previous = entries
    previous_rank = None
    for [name, rank] in zip(lineage_split, ranks_split, strict=False):

        if rank not in RANKS:
            if previous_rank == "species":
                rank = "subspecies"
            else:
                continue

        current = previous.get(name)
        if not current:
            new_entry = {"taxid": taxid, "rank": rank, "count": count, "children": {}}
            previous[name] = new_entry
            previous = new_entry["children"]
            continue

        current["count"] += count
        previous = current["children"]
        previous_rank = rank

    return entries


def yield_entries(entries, total, indent=0):
    """Get entries in printable form."""
    for i, j in entries.items():
        percent = "{:.2%}".format(j["count"] / total)
        yield (indent, i, j["taxid"], j["count"], percent, j["rank"])
        yield from yield_entries(j["children"], total, indent + 1)


def create_aggregate(sample_id: str, lineages: str, bracken: str, report: str, prefix: str, out_dir: str):
    """Run lineage aggregation algorithm."""
    bracken_counts = {}
    entries = {}
    total = 0
    with Path(bracken).open() as f:
        bracken = f.readlines()
    if len(bracken) > 0:
        for i in bracken:
            bracken_counts[i.split()[1]] = i.split()[0]
        with Path(lineages).open() as f:
            in_file = f.readlines()
        for line in in_file:
            try:
                entries = update_or_create_count(line, entries, bracken_counts)
                total += 1
            except ValueError:
                sys.stderr.write(
                    f"""Lineage for tax id {str(line)} not found in taxonomy database"""
                )
    with Path(report).open() as f:
        report_file = f.readlines()
        for line in report_file:
            if line.split()[4] == "0" and "unclassified" in line:
                unclassified_count = line.split()[2]
                entries = update_or_create_unclassified(entries, unclassified_count)
                total += int(unclassified_count)
    report_path = Path(f"{prefix}.lineages.txt")
    json_path = Path(f"{prefix}.lineages.json")

    with report_path.open("w") as report_file, json_path.open("w") as json_file:
        for indent, name, taxid, count, perc, rank in yield_entries(entries, total):
            report_file.write(
                f'{"-" * (indent + 1)} {name} {taxid} {count} {perc} {rank}\n'
            )

        json.dump(entries, json_file)
