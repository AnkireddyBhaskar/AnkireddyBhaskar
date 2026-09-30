"""Lightweight market-basket analysis (product pair association rules)."""

from __future__ import annotations

from collections import Counter
from itertools import combinations

import pandas as pd


def product_pairs(df: pd.DataFrame, min_support: float = 0.01, min_lift: float = 3.0, top_n: int = 15) -> pd.DataFrame:
    """Frequent, strongly associated product pairs ranked by support.

    Pairs must reach ``min_support`` and have a lift of at least ``min_lift``.

    Only items whose individual support is at least ``min_support`` are considered,
    which keeps the pair search tractable on ~20k invoices.
    """
    baskets = df.groupby("InvoiceNo")["Description"].apply(lambda s: sorted(set(s.dropna())))
    n = len(baskets)
    item_counts = Counter(item for basket in baskets for item in basket)
    frequent = {item for item, c in item_counts.items() if c / n >= min_support}

    pair_counts: Counter[tuple[str, str]] = Counter()
    for basket in baskets:
        items = [i for i in basket if i in frequent]
        pair_counts.update(combinations(items, 2))

    rows = []
    for (a, b), count in pair_counts.items():
        support = count / n
        if support < min_support:
            continue
        sup_a, sup_b = item_counts[a] / n, item_counts[b] / n
        lift = support / (sup_a * sup_b)
        if lift < min_lift:
            continue
        rows.append(
            {
                "item_a": a,
                "item_b": b,
                "support": support,
                "confidence_a_to_b": support / sup_a,
                "confidence_b_to_a": support / sup_b,
                "lift": lift,
            }
        )
    if not rows:
        return pd.DataFrame(columns=["item_a", "item_b", "support", "confidence_a_to_b", "confidence_b_to_a", "lift"])
    return pd.DataFrame(rows).sort_values(["support", "lift"], ascending=False).head(top_n).reset_index(drop=True)
