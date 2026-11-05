from pathlib import Path

import typer

app = typer.Typer(name="Kraken2 Detect Rank", help="Kraken2 output rank detection")

@app.command("detect-rank")
def detect_rank_commands():
    sample_id: str = type.Option(..., help="Sequence sample ID", exists=True),
    report: Path = type.Option(..., help="Path to Kraken2 reports file", exists=True),
    results: Path = type.Option(..., help="Path to Kraken2 results file", exists=True),
    database: Path = type.Option(..., help="Path to the TaxaPlease database", exists=True),
    outdir: Path = type.Option(..., help="Path to the output directory", exists=False),
    
    pass


if __name__ == "__main__":
    app()