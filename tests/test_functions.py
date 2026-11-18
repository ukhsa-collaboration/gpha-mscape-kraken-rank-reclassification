"""
Create unit tests for modules in the tests/ folder. All functions in a repo should be unit tested and
tests should be run before and after any changes are made.
"""

from pathlib import Path

import pytest  # noqa: F401
from mscape_template import mscape_functions as mf  # noqa: F401

from reclassification.data_reformatting import load_report

TEST_DATA = Path(__file__).parent / "data"


@pytest.fixture
def kraken_report():
    return TEST_DATA / "kraken_report.txt"


@pytest.fixture
def kraken_results():
    return TEST_DATA / "kraken_results.txt"


@pytest.fixture
def test_report(kraken_report):
    df = load_report(kraken_report)
    assert not df.empty


def test_report_columns(kraken_report):
    assert list(test_report.columns) == [
        "percent_coverage",
        "no_reads_covered",
        "no_reads_assigned",
        "rank",
        "taxid",
        "name",
    ]


def test_example():
    assert True
