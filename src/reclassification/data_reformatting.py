import json
import logging
import subprocess
import sys
from pathlib import Path

import pandas as pd
from onyx_analysis_helper import onyx_analysis_helper_functions as oa  # type: ignore

__version__ = "1.0.1"


ranks = ["Species", "Genus", "Family", "Order", "Kingdom", "Phylum"]
# domain = ["Archaea", "Bacteria", "Eukaryote", "Fungi", "Phage", "Virus"]


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


def which_microbe(df: pd.DataFrame, choice: str, tp_func) -> pd.DataFrame:
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
    return  outfile


def run_detection(sample_id: str, report_path: str, database_path: str, microbe:str, out_dir:str, tp_func):
    print("running")
    df = load_report(report_path=report_path)
    
    df_genus_level_detection = search_rank(df=df,
                                           rank="Genus")
    
    df_genus_level_detection = which_microbe(df=df_genus_level_detection,
                                            choice=microbe,
                                            tp_func=tp_func)
    
    df_species_level_detection = search_rank(df=df,
                                             rank="Species")
    
    df_species_level_detection = which_microbe(df=df_species_level_detection,
                                              choice=microbe,
                                              tp_func=tp_func)

    detection_json = create_json(
        sample_id=sample_id,
        rank=microbe,
        df_genus= df_genus_level_detection,
        df_species=df_species_level_detection,
        out_dir=out_dir
        )
    return detection_json
    
    
#### 


def reformat_kraken_report(sample_id: str, kraken_report: str, database_path: str, out_dir: str):
    """Replicates:

            cut -f5,3 | tail -n+3 > _taxacounts.txt
            cut -f5   | tail -n+3 > _taxa.txt
            taxonkit lineage -R _taxa.txt > _lineages.txt

        Returns:
            (_taxacounts.txt, _taxa.txt, _lineages.txt)
    """
        
    out_dir = Path(out_dir)
    taxa_file = out_dir / f"{sample_id}_taxa.txt"
    taxa_counts_file = out_dir / f"{sample_id}_taxacounts.txt"
    lineages_file = out_dir / f"{sample_id}_lineages.txt"

    bracken_counts: dict[str, int] = {}

    with (
        Path(kraken_report).open() as in_file,
        taxa_counts_file.open("w") as counts_out,
        taxa_file.open("w") as taxa_out,
    ):
        for line_number, line in enumerate(in_file):
            if line_number < 2:
                continue

            fields = line.rstrip("\n").split("\t")

            if len(fields) < 5:
                continue

            taxid = fields[4]
            count = fields[2]

            bracken_counts[taxid] = int(count)
            counts_out.write(f"{count}\t{taxid}\n")
            # counts_out.write(f"{taxid}\t{count}\n")
            taxa_out.write(f"{taxid}\n")

    with lineages_file.open("w") as lineage_out:
        subprocess.run(
            [
                "taxonkit",
                "lineage",
                "--data-dir",
                str(database_path),
                "-R",
                str(taxa_file),
            ],
            stdout=lineage_out,
            check=True,
        )

    return taxa_counts_file, taxa_file, lineages_file


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


def create_aggregate(sample_id: str, report: str, database_path: str, out_dir: str):
    
    bracken, taxa, lineages = reformat_kraken_report(sample_id=sample_id,
                                                     kraken_report=report,
                                                     database_path=database_path,
                                                     out_dir=out_dir)
    
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
                
    report_path = Path(f"{out_dir}/{sample_id}.lineages.txt")
    json_path = Path(f"{out_dir}/{sample_id}.lineages.json")

    with report_path.open("w") as report_file, json_path.open("w") as json_file:
        for indent, name, taxid, count, perc, rank in yield_entries(entries, total):
            report_file.write(
                f'{"-" * (indent + 1)} {name} {taxid} {count} {perc} {rank}\n'
            )

        json.dump(entries, json_file)
    
    return json_path
        

####


def get_id_names(in_path:str) -> [str, str]:
    climb_id = in_path.split("_")[0]
    run_id = in_path.split("_")[1]
    return climb_id, run_id


def create_analysis_fields(
    record_id: str,
    microbe: str, 
    thresholds: dict,
    pipeline_info: dict,
    results: dict,  # Optional, needs to be a dictionary
    server: str,
    headline_result: str,  # Required
    result_folder: Path,
    publish_analysis: str,
) -> dict:
    """Set up fields dictionary used to populate analysis table containing
    QC metrics.
    Arguments:
        record_id -- Climb ID for sample
        thresholds -- thresholfs used in classification
        pipeline_info -- dictionary containing Name, Version and WebURL
        headline_result -- Short description of main result/virus presence TRUE or FALSE
        results -- Dictionary containing virus reclassification results
        server -- Server code is running on, one of "mscape" or "synthscape"
    Returns:
        onyx_analysis -- Class containing required fields for input to onyx analysis table
        exitcode -- Exit code for checks - will be 0 if all checks passed, 1 if any checks failed
    """
    onyx_analysis = oa.OnyxAnalysis()
    onyx_analysis.add_analysis_details(
        analysis_name=f"gpha-mscape-orangebox-{microbe}-reclassification",
        analysis_description=f"Kraken rerun with database designed for better representation of {microbe}",
    )
    # onyx_analysis.add_package_metadata(package_name="")
    onyx_analysis.pipeline_name = pipeline_info["name"]
    onyx_analysis.pipeline_version = pipeline_info["version"]
    onyx_analysis.pipeline_url = pipeline_info["homePage"]
    
    methods_fail = onyx_analysis.add_methods(methods_dict=thresholds)
    results_fail = onyx_analysis.add_results(top_result=headline_result, results_dict=results)
    onyx_analysis.add_server_records(sample_id=record_id, server_name=server)
    # output_fail = onyx_analysis.add_output_location(result_folder)
    required_field_fail, attribute_fail = onyx_analysis.check_analysis_object(publish_analysis=False)
    
    # add in output fail to line below
    if any([methods_fail, results_fail, required_field_fail, attribute_fail]):
        logging.error("Incorrect attribute in analysis object, check logs for details")
        exitcode = 1
    else:
        logging.info("Correct attributes in analysis object")
        exitcode = 0
    return onyx_analysis, exitcode


def write_onxy_results_to_json(results_dict: dict, climb_id: str, microbe: str, results_dir: Path) -> Path:
    """Write  results dictionary to json output file.
    Arguments:
        results_dict -- Dictionary containing results
        climb_id -- CLIMB ID to use in file name
        results_dir -- Directory to save results to
    Returns:
        os.path of saved json file
    """
    result_file = Path(results_dir) / f"{climb_id}.{microbe}_reclassification.analysis_fields.json"

    with Path(result_file).open("w") as file:
        json.dump(results_dict, file)

    return result_file


def sort_pipeline_info(pipeline_info:str, microbe:str)->dict:
    pipeline_info_list = pipeline_info.split(",")
    try:
        pipeline_info_dict = {
            pipeline_info_list[0].split(":")[0]: pipeline_info_list[0].split(":")[1],  # Name
            pipeline_info_list[1].split(":")[0]: pipeline_info_list[1].split(":")[1],  # Version
            pipeline_info_list[2].split(":")[0]: ":".join(pipeline_info_list[2].split(":")[1:]),  # WebURL
        }
    except IndexError:
        pass
        print("incorrect pipeline info, list index out of range")
        pipeline_info_dict = {"name": f"{microbe}_reclassification", "version": "n/a", "homePage": "n/a"}
    return pipeline_info_dict


def create_onyx_json(climb_id: str, run_id: str, microbe: str, fastq: str, report: str, results: str, results_json: str, results_json_summary: str, pipeline_info: str, publish: str, out_dir: str):
    # Convert JSON String to Python dict
    with Path(results_json).open() as json_file:
        results_json = json.load(json_file)
    with Path(results_json_summary).open() as json_file:
        results_json_summary = json.load(json_file)

    pipeline_info_dict = sort_pipeline_info(pipeline_info=pipeline_info,
                                            microbe=microbe)

    analysis_fields_dict, exitcode = create_analysis_fields(record_id=climb_id,
                                                            microbe=microbe,
                                                            thresholds="",
                                                            pipeline_info=pipeline_info_dict,
                                                            results=results_json,  # Optional, needs to be a dictionary
                                                            server="mscape",
                                                            headline_result=results_json_summary,  # Required
                                                            result_folder="",
                                                            publish_analysis=publish)
    analysis_fields_dict.write_analysis_to_json(f"{out_dir}/{climb_id}.{microbe}_reclassification.analysis_fields.json")
    