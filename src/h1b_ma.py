"""Pipeline for the massachusetts-h1b-analysis project.

Replicates the cleaning and grouping decisions from the original analysis,
plus two portfolio additions:
  1. IT-manager exclusion: SOC "Computer and Information Systems Managers"
     is matched by title (case-insensitive), not by code, because the same
     occupation appears as 11-3021.00, 11-3021, and 11-3021.00.00 in the data.
  2. Bootstrap confidence intervals around the group medians, so the pay
     comparison is a statistical check, not just two point estimates.
"""

import numpy as np
import pandas as pd

PERIODS_PER_YEAR = {"Year": 1, "Hour": 2080, "Week": 52, "Bi-Weekly": 26, "Month": 12}

ANALYTICS_TITLES = [
    "Data Scientists",
    "Business Intelligence Analysts",
    "Operations Research Analysts",
    "Statisticians",
    "Computer Systems Analysts",
]

IT_MANAGER_TITLE = "computer and information systems managers"


def load_filings(csv_path):
    """Load the Massachusetts-filtered disclosure file (15 columns)."""
    return pd.read_csv(csv_path, low_memory=False)


def filter_certified_h1b(df):
    """Keep only H-1B filings with Certified case status."""
    return df[(df["VISA_CLASS"] == "H-1B") & (df["CASE_STATUS"] == "Certified")].copy()


def normalize_wages(df):
    """Convert every offered wage to an annual figure.

    A few rows have the pay unit recorded wrong (e.g. an annual salary tagged
    "Hour"), which the conversion blows up into impossible values. We keep
    every row and report pay with the median, which those typos can't move.
    """
    out = df.copy()
    out["annual_wage"] = (
        out["WAGE_RATE_OF_PAY_FROM"] * out["WAGE_UNIT_OF_PAY"].map(PERIODS_PER_YEAR)
    )
    return out


def assign_role_groups(df, exclude_it_managers=True):
    """Label every filing: General business, Data & analytics, or Other.

    Roles are sorted with the government's standard occupation code (SOC):
    families 11/13 are business, and five named analytics titles form the
    comparison group. Keyword matching on hand-typed job titles was rejected
    as brittle -- words like "manager" and "consultant" drag in technical
    roles the comparison doesn't want.

    With exclude_it_managers=True (the default), Computer and Information
    Systems Managers are pulled out of the business group. They are an IT
    occupation sitting inside SOC family 11, and at a $168K median they drag
    the business-group median up by $10K. Matched by title, not code, because
    the same occupation is coded three different ways in the data.
    """
    out = df.copy()
    out["soc_group"] = out["SOC_CODE"].astype(str).str[:2]
    out["role_group"] = "Other"
    out.loc[out["soc_group"].isin(["11", "13"]), "role_group"] = "General business"
    out.loc[out["SOC_TITLE"].isin(ANALYTICS_TITLES), "role_group"] = "Data & analytics"
    if exclude_it_managers:
        it_mask = out["SOC_TITLE"].str.lower() == IT_MANAGER_TITLE
        out.loc[it_mask & (out["role_group"] == "General business"), "role_group"] = (
            "Other"
        )
    out["is_stem"] = out["soc_group"].isin(["15", "17", "19"])
    return out


def summarize(df):
    """One table: filings, median annual wage, and STEM share per role group."""
    table = df.groupby("role_group").agg(
        filings=("role_group", "size"),
        median_wage=("annual_wage", "median"),
        pct_stem=("is_stem", "mean"),
    )
    table["pct_stem"] = (table["pct_stem"] * 100).round(1)
    return table


def bootstrap_median_ci(series, n_boot=2000, ci=95, seed=42):
    """Bootstrap confidence interval for the median.

    Plain-English version: resample the group's wages 2,000 times, take the
    median each time, and report the middle 95% of those medians. If the two
    groups' intervals don't overlap, the pay gap is real, not a fluke of
    which filings happened to land in the data.
    """
    rng = np.random.default_rng(seed)
    values = series.dropna().to_numpy()
    medians = np.empty(n_boot)
    for i in range(n_boot):
        medians[i] = np.median(rng.choice(values, size=len(values), replace=True))
    lower = (100 - ci) / 2
    return float(np.percentile(medians, lower)), float(np.percentile(medians, 100 - lower))
