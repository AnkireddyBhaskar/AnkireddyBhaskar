import numpy as np
import pandas as pd
import pytest

from retail_analysis import basket, data, rfm


@pytest.fixture
def synthetic_rfm() -> pd.DataFrame:
    rng = np.random.default_rng(0)
    n = 200
    return pd.DataFrame(
        {
            "Recency": rng.integers(1, 365, n),
            "Frequency": rng.integers(1, 30, n),
            "Monetary": rng.gamma(2.0, 500.0, n),
        },
        index=pd.Index(range(n), name="CustomerID"),
    )


def test_build_rfm(raw_transactions):
    table = rfm.build_rfm(data.clean(raw_transactions))
    assert list(table.index) == [1, 2, 3]
    assert table.loc[1, "Frequency"] == 2
    assert table.loc[1, "Monetary"] == pytest.approx(40)
    assert table.loc[3, "Recency"] == 0


def test_score_rfm_ranges_and_segments(synthetic_rfm):
    scored = rfm.score_rfm(synthetic_rfm)
    for col in "RFM":
        assert scored[col].between(1, 5).all()
    assert scored["Segment"].notna().all()
    best = scored.sort_values("Recency").iloc[0]
    assert best["R"] == 5


def test_segment_summary_shares(synthetic_rfm):
    summary = rfm.segment_summary(rfm.score_rfm(synthetic_rfm))
    assert summary["CustomerShare_pct"].sum() == pytest.approx(100, abs=0.1)
    assert summary["RevenueShare_pct"].sum() == pytest.approx(100, abs=0.1)


def test_kmeans_labels_ordered_by_monetary(synthetic_rfm):
    clustered = rfm.kmeans_clusters(synthetic_rfm, k=3)
    means = clustered.groupby("Cluster")["Monetary"].mean()
    assert list(means.index) == [0, 1, 2]
    assert means.is_monotonic_decreasing


def test_product_pairs():
    df = pd.DataFrame(
        {
            "InvoiceNo": ["1", "1", "2", "2", "3", "4"],
            "Description": ["TEA", "CUP", "TEA", "CUP", "LAMP", "TEA"],
        }
    )
    pairs = basket.product_pairs(df, min_support=0.3, min_lift=1.0)
    assert len(pairs) == 1
    row = pairs.iloc[0]
    assert {row["item_a"], row["item_b"]} == {"CUP", "TEA"}
    assert row["support"] == pytest.approx(0.5)
    assert row["lift"] == pytest.approx(0.5 / (0.75 * 0.5))
