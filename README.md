# Miami Heat Player Analysis

This repository contains scripts for analyzing Miami Heat player statistics and salary data for the QSAO Case Competition.

## Files

- `extract_all_data.py` - Script to extract, process, and analyze Miami Heat player data
- `extract_miami_heat.py` - Script to extract only Miami Heat players from the dataset
- `extract_miami_salary.py` - Script to extract Miami Heat players and their salary information
- `extract_miami_no_butler.py` - Script to extract Miami Heat players excluding Jimmy Butler
- `remove_butler.py` - Script to remove Jimmy Butler from the dataset

## Data Files

- `QSAO CASECOMP PLAYERDATA.xlsx` - Player statistics dataset
- `QSAO CASECOMP NBASALARY.xlsx` - Player salary information
- `Miami_Heat_Complete_Analysis.xlsx` - Processed output with combined stats and salary data

## Features

- Normalizes player names for proper matching across datasets
- Merges player stats with salary information
- Calculates team salary commitments
- Identifies top performers in various statistical categories
- Filters roster data based on custom criteria

## Usage

Run the main analysis script:

```bash
python3 extract_all_data.py
```

This will generate a complete analysis of the Miami Heat roster including statistics and salary information.

## Requirements

- Python 3.x
- pandas
- openpyxl
- unicodedata (standard library) 