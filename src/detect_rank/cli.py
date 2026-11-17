import logging
from pathlib import Path

import typer
from taxaplease.taxaplease import TaxaPlease

from detect_rank.detect_rank import create_aggregate, create_onyx_json, run_detection

app = typer.Typer(name="Kraken2 Detect Rank", help="Kraken2 output rank detection")


def normalize_choice(value: str) -> str:
    return value.strip().lower().capitalize()


# Logger set up
def set_up_logger(stdout_file):
    """Example logger set up which can be amended as required. In this example,
    all logging messages go to a stdout log file, and error messages also go to
    stderr log. If the component runs correctly, stderr is empty. The logger is
    set to append mode so logs from older runs are not overwritten.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s")

    out_handler = logging.FileHandler(stdout_file, mode="a")
    out_handler.setFormatter(formatter)
    logger.addHandler(out_handler)

    return logger


@app.command("detect-rank")
def detect_rank_commands(
    sample_id: str = typer.Option(..., help="Sequence sample ID", exists=True),
    fastq: str = typer.Option(..., help="Path to the fastq file"),
    report: str = typer.Option(..., help="Path to Kraken2 reports file", exists=True),
    results: str = typer.Option(..., help="Path to Kraken2 results file", exists=True),
    microbe: str = typer.Option(..., help="Microbe to search for", exists=True, callback=normalize_choice),
    tp_database: str = typer.Option(..., help="Path to the TaxaPlease database", exists=True),
    ncbi_database: str = typer.Option(..., help="Path to the NCBI taxonomy directory.", exists=True),
    out_dir: str = typer.Option(..., help="Path to the output directory", exists=False)
    ):
    
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(f"{out_dir}/logfile.txt")
    set_up_logger(log_file)
    
    taxaPlease = TaxaPlease(database=tp_database)

    microbe_choices, tp_func = validate_microbe(
        microbe=microbe,
        taxaPlease=taxaPlease
        )
    
    detection_json = run_detection(
        sample_id=sample_id,
        report_path=report,
        database_path=tp_database,
        microbe=microbe,
        out_dir=out_dir,
        tp_func=tp_func
        )
    
    scylla_json = create_aggregate(
        sample_id=sample_id,
        report=report,
        database_path=ncbi_database,
        out_dir=out_dir,
    )
    
    create_onyx_json(
        climb_id=sample_id,
        run_id="", 
        microbe=microbe, 
        fastq=fastq, 
        report=report, 
        results=results, 
        results_json=detection_json, 
        results_json_summary=scylla_json,
        pipeline_info=""
        )
    

def validate_microbe(microbe:str, taxaPlease):
    allowed_choices = {
        method[2:].lower(): getattr(taxaPlease, method)
        for method in dir(taxaPlease)
        if method.startswith("is")
        and callable(getattr(taxaPlease, method))
    }

    choice = microbe.lower()
    
    if choice not in allowed_choices:
        raise typer.BadParameter(
            f"Invalid choice '{choice}'. "
            f"Allowed values: {', '.join(sorted(allowed_choices))}"
        )
        
    tp_func = allowed_choices[choice]
    return allowed_choices, tp_func


@app.command("aggregate-results")
def aggregate_results_commands(
    sample_id: str = typer.Option(..., help="Sequence sample ID.", exists=True),
    # lineages: str = typer.Option(..., help="Lineages .tsv (taxid, lineage).", exists=True),
    # bracken: str = typer.Option(..., help="Bracken Lineages .tsv (taxid, count).", exists=True),
    report: str = typer.Option(..., help="Path to Kraken2 reports file.", exists=True),
    database_path: str = typer.Option(..., help="Path to the NCBI taxonomy directory.", exists=True),
    out_dir: str = typer.Option(..., help="Path to the output directory.", exists=False)
    ):
    """Parse command line arguments and run main."""
    
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    create_aggregate(
        sample_id=sample_id,
        report=report,
        database_path=database_path,
        out_dir=out_dir,
    )


@app.command("onyx-results")
def generate_onyx_json(
    sample_id: str = typer.Option(..., help="Sequence sample ID.", exists=True),
    lineages: str = typer.Option(..., help="Lineages .tsv (taxid, lineage).", exists=True),
    bracken: str = typer.Option(..., help="Bracken Lineages .tsv (taxid, count).", exists=True),
    report: str = typer.Option(..., help="Path to Kraken2 reports file.", exists=True),
    out_dir: str = typer.Option(..., help="Path to the output directory.", exists=False)
    ):
    pass

if __name__ == "__main__":
    app()