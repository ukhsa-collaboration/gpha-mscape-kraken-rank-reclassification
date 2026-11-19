# <img src="assests/UKHSA_Logo.png" width="75" alt="UKHSA Logo"> GPHA mSCAPE Kraken Rank Classification

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
| Author(s)    | GPHA                                                                                |
| Summary      | Search Kraken output reports.txt for microbe and reformat to match Syclla reporting |

---

## Features

- aggregate-results function
  - produces Scylla formatted json of Kraken report
- run-reclassification function
  - uses TaxaPlease to search for microorganism family in Kraken report file

---

## Requirements
>
> [!Warning]
> TaxaPlease database
> NCBI taxonkit database
---

## Install

- Login to BRYN
- Start a terminal session
- Navigate to desired parent directory
- Run:

```bash
git clone git@github.com:ukhsa-collaboration/gpha-mscape-kraken-rank-reclassification.git
cd gpha-mscape-kraken-rank-reclassification
conda create -n k-squared
conda activate k-squared
pip install .
mamba install -c bioconda taxonkit
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
classify run-reclassification --sample-id <id/prefix> --report <path-to-kraken_report.txt> --results <path-to-kraken_results.txt> --out-dir <save-directory> --microbe <archaea/bacteria/fungi/protozoa/virus> --tp_database <path-to-taxaplease-database/taxa.db> --ncbi_database <path-to-NCBI-database> --publish <currently not fully functional required for pushing to onyx>
```

- For Scylla formatted json:

```bash
classify aggregate-results --sample-id <id/prefix> --lineages <path-to-modified_report_lineages.txt> --bracken <path-to-modified_report_taxacounts.txt> --report <path-to-kraken_report.txt --out-dir <save-directory>
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

---

## Change-log

See CHANGELOG.md

---

## To-do

- [x] update feature section in README.md
- [ ] \(Optional) add collapsing functionality to sections/components
- [ ] \(Optional) task

---
