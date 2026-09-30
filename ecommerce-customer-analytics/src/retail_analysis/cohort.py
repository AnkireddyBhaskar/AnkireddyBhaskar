"""Monthly acquisition-cohort retention analysis."""

from __future__ import annotations

import pandas as pd


def cohort_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Active customers per acquisition cohort (rows) and months since first purchase (columns)."""
    known = df.dropna(subset=["CustomerID"])[["CustomerID", "InvoiceMonth"]].drop_duplicates()
    known["Cohort"] = known.groupby("CustomerID")["InvoiceMonth"].transform("min")
    known["CohortIndex"] = (known["InvoiceMonth"] - known["Cohort"]).apply(lambda offset: offset.n)
    return known.pivot_table(index="Cohort", columns="CohortIndex", values="CustomerID", aggfunc="nunique")


def retention_matrix(df: pd.DataFrame) -> pd.DataFrame:
    """Share of each cohort still purchasing N months after acquisition."""
    counts = cohort_counts(df)
    return counts.divide(counts[0], axis=0)
