# Data

## Source

[H1B LCA Disclosure Data (2020–2024)](https://www.kaggle.com/datasets/zongaobian/h1b-lca-disclosure-data-2020-2024) — U.S. Department of Labor Labor Condition Application disclosure data, FY2020 through FY2024, published on Kaggle as one file per year.

## How to reproduce the input file

The notebook expects this file at `data/ma_h1b_fy2020_2024.csv` (it is **not** checked into git — see `.gitignore`). To build it:

1. Download the combined file `Combined_LCA_Disclosure_Data_FY2020_to_FY2024.csv` from the Kaggle dataset above (free Kaggle account required; ~2.82 GB, 96 columns).
2. Keep rows where `WORKSITE_STATE == 'MA'`.
3. Keep 15 of the 96 columns: `CASE_STATUS`, `VISA_CLASS`, `JOB_TITLE`, `SOC_CODE`, `SOC_TITLE`, `FULL_TIME_POSITION`, `EMPLOYER_NAME`, `NAICS_CODE`, `WORKSITE_CITY`, `WORKSITE_STATE`, `WAGE_RATE_OF_PAY_FROM`, `WAGE_UNIT_OF_PAY`, `PREVAILING_WAGE`, `PW_WAGE_LEVEL`, `FISCAL_YEAR`.
4. Save as `data/ma_h1b_fy2020_2024.csv`. You should get 137,866 rows.

Everything downstream — filtering to certified H-1B filings, wage normalization, role grouping — happens in the notebook via `../src/h1b_ma.py`.
