import typer

app = typer.Typer(name="Kraken2 Detect Rank", help="Kraken2 output rank detection")

@app.command("detect-rank")
def detect_rank_commands():
    pass


if __name__ == "__main__":
    app()