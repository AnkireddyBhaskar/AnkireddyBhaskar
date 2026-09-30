"""End-to-end analysis pipeline: clean data, compute insights, save figures and tables."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from . import basket, cohort, data, metrics, plots, rfm

ROOT = Path(__file__).resolve().parents[2]
FIG_DIR = ROOT / "reports" / "figures"
TABLE_DIR = ROOT / "reports" / "tables"

CLUSTER_NAMES = {0: "VIP", 1: "Loyal", 2: "Occasional", 3: "Lapsed"}


def run(k: int = 4) -> dict[str, object]:
    raw = data.load_raw()
    df = data.clean(raw)
    TABLE_DIR.mkdir(parents=True, exist_ok=True)

    report = data.cleaning_report(raw, df)
    kpis = metrics.kpis(df)
    monthly = metrics.monthly_revenue(df)
    top = metrics.top_products(df)
    countries = metrics.revenue_by_country(df)
    heat = metrics.weekday_hour_heatmap(df)
    pareto = metrics.pareto_share(df)

    retention = cohort.retention_matrix(df)

    rfm_table = rfm.build_rfm(df)
    scored = rfm.score_rfm(rfm_table)
    seg_summary = rfm.segment_summary(scored)
    k_scores = rfm.choose_k(rfm_table)
    clustered = rfm.kmeans_clusters(rfm_table, k=k)
    cluster_profile = clustered.groupby("Cluster").agg(
        Customers=("Recency", "size"),
        AvgRecency=("Recency", "mean"),
        AvgFrequency=("Frequency", "mean"),
        AvgMonetary=("Monetary", "mean"),
        TotalRevenue=("Monetary", "sum"),
    )
    cluster_profile["RevenueShare_pct"] = 100 * cluster_profile["TotalRevenue"] / cluster_profile["TotalRevenue"].sum()
    if k == len(CLUSTER_NAMES):
        cluster_profile.insert(0, "Name", cluster_profile.index.map(CLUSTER_NAMES))
    cluster_profile = cluster_profile.round(2)

    pairs = basket.product_pairs(df)

    plots.monthly_revenue(monthly, FIG_DIR / "01_monthly_revenue.png")
    plots.top_products(top, FIG_DIR / "02_top_products.png")
    plots.country_revenue(countries, FIG_DIR / "03_country_revenue.png")
    plots.weekday_hour(heat, FIG_DIR / "04_weekday_hour_heatmap.png")
    plots.cohort_retention(retention, FIG_DIR / "05_cohort_retention.png")
    plots.rfm_segments(seg_summary, FIG_DIR / "06_rfm_segments.png")
    plots.k_selection(k_scores, FIG_DIR / "07_kmeans_k_selection.png")
    hue = "Cluster"
    if k == len(CLUSTER_NAMES):
        clustered["ClusterName"] = pd.Categorical(clustered["Cluster"].map(CLUSTER_NAMES), categories=CLUSTER_NAMES.values())
        hue = "ClusterName"
    plots.clusters(clustered, FIG_DIR / "08_customer_clusters.png", hue=hue)

    report.to_csv(TABLE_DIR / "cleaning_report.csv", header=["value"])
    kpis.to_csv(TABLE_DIR / "kpis.csv", header=["value"])
    monthly.round(2).to_csv(TABLE_DIR / "monthly_revenue.csv")
    top.round(2).to_csv(TABLE_DIR / "top_products.csv", index=False)
    countries.round(2).to_csv(TABLE_DIR / "country_revenue.csv")
    retention.round(4).to_csv(TABLE_DIR / "cohort_retention.csv")
    seg_summary.to_csv(TABLE_DIR / "rfm_segment_summary.csv")
    cluster_profile.to_csv(TABLE_DIR / "cluster_profile.csv")
    pairs.round(4).to_csv(TABLE_DIR / "product_pairs.csv", index=False)

    return {
        "cleaning": report,
        "kpis": kpis,
        "pareto_top20_pct": pareto,
        "monthly": monthly,
        "countries": countries,
        "retention_month1_avg": retention[1].mean(),
        "segments": seg_summary,
        "k_scores": k_scores,
        "clusters": cluster_profile,
        "pairs": pairs,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k", type=int, default=4, help="number of K-Means clusters")
    args = parser.parse_args()
    pd.set_option("display.width", 160)
    pd.set_option("display.max_columns", 20)
    results = run(k=args.k)
    for name, value in results.items():
        print(f"\n=== {name} ===\n{value}")
    print(f"\nFigures saved to {FIG_DIR}\nTables saved to {TABLE_DIR}")


if __name__ == "__main__":
    main()
