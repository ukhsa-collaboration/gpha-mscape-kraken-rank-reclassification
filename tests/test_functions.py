"""
Create unit tests for modules in the tests/ folder. All functions in a repo should be unit tested and
tests should be run before and after any changes are made.
"""

from pathlib import Path

import pytest  # noqa: F401
from mscape_template import mscape_functions as mf  # noqa: F401

from reclassification.data_reformatting import load_report, search_rank

TEST_DATA = Path(__file__).parent / "data"


@pytest.fixture
def kraken_report():
    return TEST_DATA / "test_kraken_report.txt"


@pytest.fixture
def kraken_results():
    return TEST_DATA / "test_kraken_results.txt"


@pytest.fixture
def test_report(kraken_report):
    df = load_report(kraken_report)
    assert not df.empty
    return df


def test_report_columns(test_report):
    assert list(test_report.columns) == [
        "percent_coverage",
        "no_reads_covered",
        "no_reads_assigned",
        "rank",
        "taxid",
        "name",
    ]


@pytest.fixture
def test_search_rank_genus(test_report):
    df = search_rank(test_report, "Genus") 
    print(df)
    assert not df.empty
    assert df["rank"].nunique() == 1
    assert df["taxid"].nunique() == 3
    assert df["name"].nunique() == 3
    assert set(df["rank"]) == {"G"}
    assert set(df["taxid"] == {561, 11118, 4932})
    assert set(df["name"]) == {"Escherichia", "Betacoronavirus", "Saccharomyces"}
    
    return df


@pytest.fixture
def test_search_rank_species(test_report):    
    df = search_rank(test_report, "Species")
    print(df)
    assert not df.empty
    assert df["rank"].nunique() == 1
    assert df["taxid"].nunique() == 3
    assert df["name"].nunique() == 3
    assert set(df["rank"]) == {"S"}
    assert set(df["taxid"] == {562, 2697049, 4932})
    assert set(df["name"]) == {"Escherichia coli", "Saccharomyces cerevisiae", "Severe acute respiratory syndrome coronavirus 2"}
    return df


# def test_which_microbe(test_search_rank_genus):
#     df = which_microbe(test_search_rank_genus)