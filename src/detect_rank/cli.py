from pathlib import Path

import typer
from taxaplease.taxaplease import TaxaPlease

from detect_rank.detect_rank import run_detection

app = typer.Typer(name="Kraken2 Detect Rank", help="Kraken2 output rank detection")


def normalize_choice(value: str) -> str:
    return value.strip().lower().capitalize()


@app.command("detect-rank")
def detect_rank_commands(
    sample_id: str = typer.Option(..., help="Sequence sample ID", exists=True),
    report: str = typer.Option(..., help="Path to Kraken2 reports file", exists=True),
    results: str = typer.Option(..., help="Path to Kraken2 results file", exists=True),
    family: str = typer.Option(..., help="Family to search for", exists=True, callback=normalize_choice),
    database: str = typer.Option(..., help="Path to the TaxaPlease database", exists=True),
    outdir: str = typer.Option(..., help="Path to the output directory", exists=False)
    ):
    
    
    taxaPlease = TaxaPlease(database=database)

    family_choices, tp_func = validate_family(family=family,
                                              taxaPlease=taxaPlease)
    
    run_detection(sample_id=sample_id,
                  report_path=report,
                  database_path=database,
                  family=family,
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


if __name__ == "__main__":
    app()