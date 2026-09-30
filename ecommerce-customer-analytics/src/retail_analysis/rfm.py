"""RFM (Recency, Frequency, Monetary) segmentation and K-Means clustering."""

from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

SEGMENT_RULES: list[tuple[str, str]] = [
    ("Champions", r"[4-5][4-5]"),
    ("Loyal Customers", r"[3-5][3-5]"),
    ("Potential Loyalists", r"[4-5][2-3]"),
    ("New Customers", r"[4-5]1"),
    ("Need Attention", r"3[1-2]"),
    ("At Risk", r"[1-2][3-5]"),
    ("Hibernating", r"[1-2][1-2]"),
]


def build_rfm(df: pd.DataFrame, snapshot_date: pd.Timestamp | None = None) -> pd.DataFrame:
    """Compute Recency (days), Frequency (orders) and Monetary (revenue) per customer."""
    known = df.dropna(subset=["CustomerID"])
    if snapshot_date is None:
        snapshot_date = known["InvoiceDate"].max().normalize() + pd.Timedelta(days=1)
    rfm = known.groupby("CustomerID").agg(
        Recency=("InvoiceDate", lambda s: (snapshot_date - s.max()).days),
        Frequency=("InvoiceNo", "nunique"),
        Monetary=("Revenue", "sum"),
    )
    return rfm


def score_rfm(rfm: pd.DataFrame, bins: int = 5) -> pd.DataFrame:
    """Add quintile scores (1-5, higher is better) and a rule-based segment label."""
    out = rfm.copy()
    out["R"] = pd.qcut(out["Recency"].rank(method="first"), bins, labels=range(bins, 0, -1)).astype(int)
    out["F"] = pd.qcut(out["Frequency"].rank(method="first"), bins, labels=range(1, bins + 1)).astype(int)
    out["M"] = pd.qcut(out["Monetary"].rank(method="first"), bins, labels=range(1, bins + 1)).astype(int)
    out["RFM_Score"] = out["R"].astype(str) + out["F"].astype(str) + out["M"].astype(str)
    rf = out["R"].astype(str) + out["F"].astype(str)
    out["Segment"] = "Other"
    for name, pattern in reversed(SEGMENT_RULES):
        out.loc[rf.str.fullmatch(pattern), "Segment"] = name
    return out


def segment_summary(scored: pd.DataFrame) -> pd.DataFrame:
    """Size, average RFM values and revenue share for each segment."""
    summary = scored.groupby("Segment").agg(
        Customers=("Recency", "size"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        AvgMonetary=("Monetary", "mean"),
        TotalRevenue=("Monetary", "sum"),
    )
    summary["CustomerShare_pct"] = 100 * summary["Customers"] / summary["Customers"].sum()
    summary["RevenueShare_pct"] = 100 * summary["TotalRevenue"] / summary["TotalRevenue"].sum()
    return summary.sort_values("TotalRevenue", ascending=False).round(2)


def _features(rfm: pd.DataFrame) -> np.ndarray:
    logged = np.log1p(rfm[["Recency", "Frequency", "Monetary"]].clip(lower=0))
    return StandardScaler().fit_transform(logged)


def choose_k(rfm: pd.DataFrame, k_range: range = range(2, 9), random_state: int = 42) -> pd.DataFrame:
    """Inertia (elbow) and silhouette score for each candidate k."""
    x = _features(rfm)
    rows = []
    for k in k_range:
        model = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(x)
        rows.append({"k": k, "inertia": model.inertia_, "silhouette": silhouette_score(x, model.labels_)})
    return pd.DataFrame(rows).set_index("k")


def kmeans_clusters(rfm: pd.DataFrame, k: int = 4, random_state: int = 42) -> pd.DataFrame:
    """Cluster customers on log-scaled, standardised RFM features.

    Clusters are relabelled 0..k-1 in descending order of average monetary value
    so labels are stable and interpretable.
    """
    x = _features(rfm)
    labels = KMeans(n_clusters=k, n_init=10, random_state=random_state).fit_predict(x)
    out = rfm.copy()
    out["Cluster"] = labels
    order = out.groupby("Cluster")["Monetary"].mean().sort_values(ascending=False).index
    out["Cluster"] = out["Cluster"].map({old: new for new, old in enumerate(order)})
    return out
