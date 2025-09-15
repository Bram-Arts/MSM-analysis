# My Singing Monsters analysis 

## Disclaimer

This is a work in progress! Make sure to pull for the latest changes regularly.

### Features

Current features:

- Imports live breeding data from the master sheet as a pandas dataframe, based on https://github.com/TRGRally/msm-data-cleaner
- For each datapoint, determines all possible results for those parents at that time
- Separate files containing monster elements, breeding combinations and special event availability

Planned features:

- Lining up output files with master sheet, for further analysis in Google Sheets
- Using CSV inputs instead of some arbitrary format in a .txt file
- Data selecting features, to e.g. select all paironormal attempts
- Data analysis features, to figure out torches, levels, parents etc. work

### Usage

1. Python, pandas, numpy required
2. Choose Excel or csv output (openpyxl required for Excel output)
2. Run "main.py"
4. "possible_results.xlsx/.csv" should be created in the same directory. Since some data cleaning took place, entries will not completely line up with the original datasheet.