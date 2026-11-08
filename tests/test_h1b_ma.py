"""Checks on the cleaning and grouping rules in src/h1b_ma.py.

Each test builds a few hand-made filings, so the expected answer is known
exactly and the tests run in under a second without the 22MB data file.
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
import h1b_ma  # noqa: E402


def test_filter_keeps_only_certified_h1b():
    df = pd.DataFrame({
        "VISA_CLASS": ["H-1B", "H-1B", "E-3 Australian", "H-1B1 Singapore", "H-1B"],
        "CASE_STATUS": ["Certified", "Denied", "Certified", "Certified", "Withdrawn"],
    })
    kept = h1b_ma.filter_certified_h1b(df)
    assert len(kept) == 1
    assert kept.iloc[0].to_dict() == {"VISA_CLASS": "H-1B", "CASE_STATUS": "Certified"}


@pytest.mark.parametrize("rate, unit, expected", [
    (95_000, "Year", 95_000),
    (50, "Hour", 104_000),        # 2,080 working hours a year
    (2_000, "Week", 104_000),
    (4_000, "Bi-Weekly", 104_000),
    (8_000, "Month", 96_000),
])
def test_wages_are_annualized_by_pay_unit(rate, unit, expected):
    df = pd.DataFrame({"WAGE_RATE_OF_PAY_FROM": [rate], "WAGE_UNIT_OF_PAY": [unit]})
    assert h1b_ma.normalize_wages(df)["annual_wage"].iloc[0] == expected


def test_unknown_pay_unit_becomes_missing_instead_of_a_wrong_number():
    df = pd.DataFrame({"WAGE_RATE_OF_PAY_FROM": [70_000], "WAGE_UNIT_OF_PAY": ["Fortnight"]})
    assert np.isnan(h1b_ma.normalize_wages(df)["annual_wage"].iloc[0])


def test_it_managers_leave_the_business_group_in_all_three_code_formats():
    # The same occupation is coded three ways in the source data, and the
    # title casing varies, so the exclusion has to match on the title.
    df = pd.DataFrame({
        "SOC_CODE": ["11-3021.00", "11-3021", "11-3021.00.00", "11-1021.00", "13-1111.00", "15-2051.00"],
        "SOC_TITLE": [
            "Computer and Information Systems Managers",
            "COMPUTER AND INFORMATION SYSTEMS MANAGERS",
            "computer and information systems managers",
            "General and Operations Managers",
            "Management Analysts",
            "Data Scientists",
        ],
    })
    grouped = h1b_ma.assign_role_groups(df)
    assert grouped["role_group"].tolist() == [
        "Other", "Other", "Other", "General business", "General business", "Data & analytics",
    ]

    kept_in = h1b_ma.assign_role_groups(df, exclude_it_managers=False)
    assert (kept_in["role_group"].iloc[:3] == "General business").all()


def test_bootstrap_interval_brackets_the_median_and_is_reproducible():
    wages = pd.Series([60_000, 72_000, 85_000, 90_000, 110_000, 125_000, 150_000])
    low, high = h1b_ma.bootstrap_median_ci(wages, n_boot=500)
    assert low <= wages.median() <= high
    assert (low, high) == h1b_ma.bootstrap_median_ci(wages, n_boot=500)
