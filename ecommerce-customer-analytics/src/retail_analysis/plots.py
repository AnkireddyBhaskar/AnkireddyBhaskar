"""Plotting helpers that save publication-ready figures."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import seaborn as sns

sns.set_theme(style="whitegrid", palette="deep")
GBP = mtick.FuncFormatter(lambda x, _: f"£{x / 1e3:,.0f}k")


def _save(fig: plt.Figure, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(fig)
    return path


def monthly_revenue(monthly: pd.DataFrame, path: Path) -> Path:
    fig, ax1 = plt.subplots(figsize=(11, 5))
    x = monthly.index.astype(str)
    ax1.bar(x, monthly["revenue"], color=sns.color_palette()[0], alpha=0.85, label="Revenue")
    ax1.yaxis.set_major_formatter(GBP)
    ax1.set_ylabel("Revenue")
    ax1.tick_params(axis="x", rotation=45)
    ax2 = ax1.twinx()
    ax2.plot(x, monthly["customers"], color=sns.color_palette()[3], marker="o", label="Active customers")
    ax2.set_ylabel("Active customers")
    ax2.grid(False)
    ax1.set_title("Monthly revenue and active customers (Dec 2010 – Dec 2011*)")
    fig.legend(loc="upper center", bbox_to_anchor=(0.45, 0.9), ncol=2)
    fig.text(0.01, -0.02, "*December 2011 contains only 9 days of data.", fontsize=8, color="grey")
    return _save(fig, path)


def top_products(top: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(10, 5.5))
    labels = top["Description"].str.title().str.slice(0, 38)
    sns.barplot(x=top["Revenue"], y=labels, ax=ax, color=sns.color_palette()[2])
    ax.xaxis.set_major_formatter(GBP)
    ax.set_xlabel("Revenue")
    ax.set_ylabel("")
    ax.set_title("Top 10 products by revenue")
    return _save(fig, path)


def country_revenue(countries: pd.DataFrame, path: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    sns.barplot(x=countries["Revenue"], y=countries.index, ax=axes[0], color=sns.color_palette()[0])
    axes[0].xaxis.set_major_formatter(GBP)
    axes[0].set_title("Top 10 countries by revenue")
    axes[0].set_ylabel("")
    non_uk = countries.drop(index="United Kingdom", errors="ignore")
    sns.barplot(x=non_uk["Revenue"], y=non_uk.index, ax=axes[1], color=sns.color_palette()[1])
    axes[1].xaxis.set_major_formatter(GBP)
    axes[1].set_title("International markets (excluding UK)")
    axes[1].set_ylabel("")
    return _save(fig, path)


def weekday_hour(heatmap: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(12, 4.5))
    sns.heatmap(heatmap, cmap="YlOrRd", ax=ax, cbar_kws={"label": "Orders"}, linewidths=0.3)
    ax.set_title("When do customers order? (orders by weekday and hour)")
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("")
    return _save(fig, path)


def cohort_retention(retention: pd.DataFrame, path: Path) -> Path:
    fig, ax = plt.subplots(figsize=(13, 7))
    data = retention.copy()
    data.index = data.index.astype(str)
    sns.heatmap(
        data, annot=True, fmt=".0%", cmap="Blues", ax=ax, vmin=0, vmax=0.5, cbar_kws={"format": mtick.PercentFormatter(1.0)}
    )
    ax.set_title("Monthly cohort retention (share of customers returning N months after first purchase)")
    ax.set_xlabel("Months since first purchase")
    ax.set_ylabel("Acquisition cohort")
    return _save(fig, path)


def rfm_segments(summary: pd.DataFrame, path: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    ordered = summary.sort_values("Customers", ascending=True)
    axes[0].barh(ordered.index, ordered["CustomerShare_pct"], color=sns.color_palette()[0])
    axes[0].set_title("Share of customers by RFM segment")
    axes[0].xaxis.set_major_formatter(mtick.PercentFormatter())
    axes[1].barh(ordered.index, ordered["RevenueShare_pct"], color=sns.color_palette()[2])
    axes[1].set_title("Share of revenue by RFM segment")
    axes[1].xaxis.set_major_formatter(mtick.PercentFormatter())
    axes[1].set_yticklabels([])
    return _save(fig, path)


def k_selection(scores: pd.DataFrame, path: Path) -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(11, 4))
    axes[0].plot(scores.index, scores["inertia"], marker="o")
    axes[0].set_title("Elbow method")
    axes[0].set_xlabel("k")
    axes[0].set_ylabel("Inertia")
    axes[1].plot(scores.index, scores["silhouette"], marker="o", color=sns.color_palette()[3])
    axes[1].set_title("Silhouette score")
    axes[1].set_xlabel("k")
    return _save(fig, path)


def clusters(clustered: pd.DataFrame, path: Path, hue: str = "Cluster") -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    palette = sns.color_palette("deep", clustered[hue].nunique())
    sns.scatterplot(data=clustered, x="Recency", y="Monetary", hue=hue, palette=palette, alpha=0.6, s=18, ax=axes[0])
    axes[0].set_yscale("log")
    axes[0].legend(title="Cluster")
    axes[0].set_title("Customer clusters: recency vs. monetary value")
    axes[0].set_xlabel("Days since last purchase")
    axes[0].set_ylabel("Total spend (£, log scale)")
    sns.scatterplot(
        data=clustered, x="Frequency", y="Monetary", hue=hue, palette=palette, alpha=0.6, s=18, ax=axes[1], legend=False
    )
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_title("Customer clusters: frequency vs. monetary value")
    axes[1].set_xlabel("Number of orders (log scale)")
    axes[1].set_ylabel("")
    return _save(fig, path)
