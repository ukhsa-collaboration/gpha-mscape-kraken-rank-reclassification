# <img src="https://upload.wikimedia.org/wikipedia/fi/6/69/UKHSA_Logo.svg.png" alt="mSCAPE logo" width="75" height="75"> GPHA mSCAPE Kraken Rank Classification

## Table of Contents

- [ GPHA mSCAPE Kraken Rank Classification](#-gpha-mscape-kraken-rank-classification)
  - [Table of Contents](#table-of-contents)
  - [Info](#info)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Install](#install)
  - [Usage](#usage)
    - [To run the application](#to-run-the-application)
    - [Commands](#commands)
  - [Troubleshooting](#troubleshooting)
  - [Change-log](#change-log)
  - [To-do](#to-do)

---

## Info

| Name         | mSCAPE-Kraken-Rank-Reclassification                                                 |
|--------------|-------------------------------------------------------------------------------------|
| Version      | 1.0.1                                                                               |
| Last Updated | 13.11.2026                                                                          |
| Author(s)    | Mike Brown                                                                          |
| Contact      | <michael.d.brown@ukhsa.gov.uk>                                                      |
| Summary      | Rank classification and json output generation (Syclla format) of Kraken reports    |

---

## Features

- aggregate-results function
- detect-rank function
  - uses TaxaPlease to search for microorganism family in Kraken report file

---

## Requirements
>
> [!Warning]
> To run (as part of mSCAPE pipelines) it is necessary to have obtained: <br>
> Access to BRYN <br>
---

## Install

- Login to BRYN
- Start a terminal session
- Navigate to desired parent directory
- Run:

```bash
git clone git@github.com:ukhsa-collaboration/gpha-mscape-kraken-rank-reclassification.git
cd gpha-mscape-kraken-rank-reclassification
conda create -n kraken-reports
conda activate kraken-reports
pip install .
```

> [!Tip]
> To run in developer mode:
>
> ```bash
> pip install --editable '.[dev]'
> ```

---

## Usage

### To run the application

- Activate the environment
- For Family Search:

```bash
find-rank detect-rank --sample-id <id/prefix> --report <path-to-kraken_report.txt> --results <path-to-kraken_results.txt> --database <path-to-taxaplease-database/taxa.db> --out-dir <save-directory> --family <archaea/bacteria/fungi/protozoa/virus> 
```

- For Scylla formatted json:

```bash
find-rank aggregate-results --sample-id <id/prefix> --lineages <path-to-modified_report_lineages.txt> --bracken <path-to-modified_report_taxacounts.txt> --report <path-to-kraken_report.txt --out-dir <save-directory>
```

> [!Note]
> To obtain lineages.txt and taxacounts.txt
>
> ```bash
> cat "${kraken_report}" | cut -f5,3 | tail -n+3 > "_taxacounts.txt"
> cat "${kraken_report}" | cut -f5 | tail -n+3 > "_taxa.txt"
> taxonkit lineage --data-dir "${db_path}" -R "_taxa.txt"  > "_lineages.txt"
> ```
>
> where db_path is the path to NCBI Taxonomy dump files

### Commands

> [!Note]
> To view commands --help/-h

| Argument | Required | Description | Default |
| -------- | ------- | ------- | ----- |
| find-rank | No | select family search  | n/a |
| aggregate-results | No | select Scylla reformatting | n/a |
| sample-id | Yes | ID of sample (prefix of output files) | n/a |
| report | Yes | path to kraken report.txt file | n/a |
| out-dir | Yes | path to the output save directory | n/a |
| family | if find-rank | selection of family (archaea/bacteria/fungi/protozoa/virus) for filtering | n/a |
| database | if find-rank | path to TaxaPlease database | n/a |
| lineages | if aggregate-lineages | path to custom kraken report _lineages.txt | n/a |
| bracken | if aggregate-lineages | path to custom kraken report _taxacounts.txt | n/a |
| --help, -h | No | show the help message and exit | |

---

## Troubleshooting

> [!Important]
> Make sure to activate the correct environment to avoid errors <br>
> Make sure all paths are entered correctly (Note. as of version 0.1.0 there is no config validation function/s) <br>
> Make sure to see notes on how to obtain lineages.txt and taxacounts.txt

---

## Change-log

See CHANGELOG.md

---

## To-do

- [x] update feature section in README.md
- [ ] \(Optional) add collapsing functionality to sections/components
- [ ] \(Optional) task

---
