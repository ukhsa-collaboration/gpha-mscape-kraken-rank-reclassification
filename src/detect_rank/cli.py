from pathlib import Path

import typer

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
    
    run_detection(sample_id=sample_id,
                  report_path=report,
                  database_path=database,
                  family=family)


if __name__ == "__main__":
    app()