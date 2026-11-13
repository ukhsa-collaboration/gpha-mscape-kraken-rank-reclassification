import logging
from pathlib import Path

import typer
from taxaplease.taxaplease import TaxaPlease

from detect_rank.detect_rank import create_aggregate, run_detection

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
    report: str = typer.Option(..., help="Path to Kraken2 reports file", exists=True),
    results: str = typer.Option(..., help="Path to Kraken2 results file", exists=True),
    family: str = typer.Option(..., help="Family to search for", exists=True, callback=normalize_choice),
    database: str = typer.Option(..., help="Path to the TaxaPlease database", exists=True),
    out_dir: str = typer.Option(..., help="Path to the output directory", exists=False)
    ):
    
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    log_file = Path(f"{out_dir}/logfile.txt")
    set_up_logger(log_file)
    
    taxaPlease = TaxaPlease(database=database)

    family_choices, tp_func = validate_family(family=family,
                                              taxaPlease=taxaPlease)
    
    run_detection(sample_id=sample_id,
                  report_path=report,
                  database_path=database,
                  family=family,
                  out_dir=out_dir,
                  tp_func=tp_func)
    

def validate_family(family:str, taxaPlease):
    allowed_choices = {
        method[2:].lower(): getattr(taxaPlease, method)
        for method in dir(taxaPlease)
        if method.startswith("is")
        and callable(getattr(taxaPlease, method))
    }

    choice = family.lower()
    
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
    lineages: str = typer.Option(..., help="Lineages .tsv (taxid, lineage).", exists=True),
    bracken: str = typer.Option(..., help="Bracken Lineages .tsv (taxid, count).", exists=True),
    report: str = typer.Option(..., help="Path to Kraken2 reports file.", exists=True),
    out_dir: str = typer.Option(..., help="Path to the output directory.", exists=False)
    ):
    """Parse command line arguments and run main."""
    
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    
    create_aggregate(
        sample_id=sample_id,
        lineages=lineages,
        bracken=bracken,
        report=report,
        out_dir=out_dir,
    )



if __name__ == "__main__":
    app()