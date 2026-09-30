import pytest

from retail_analysis import cohort, data, metrics


@pytest.fixture
def cleaned(raw_transactions):
    return data.clean(raw_transactions)


def test_kpis(cleaned):
    k = metrics.kpis(cleaned)
    assert k["total_revenue"] == pytest.approx(20 + 20 + 5 + 30 + 50 + 5)
    assert k["orders"] == 5
    assert k["customers"] == 3
    assert k["repeat_customer_rate_pct"] == pytest.approx(100 / 3, abs=0.01)


def test_monthly_revenue_sums_to_total(cleaned):
    monthly = metrics.monthly_revenue(cleaned)
    assert monthly["revenue"].sum() == pytest.approx(cleaned["Revenue"].sum())
    assert list(monthly.index.astype(str)) == ["2011-01", "2011-02", "2011-03"]


def test_revenue_by_country_shares(cleaned):
    countries = metrics.revenue_by_country(cleaned)
    assert countries["Share_pct"].sum() == pytest.approx(100)
    assert countries.index[0] == "Germany"


def test_pareto_share(cleaned):
    assert metrics.pareto_share(cleaned, top_fraction=0.34) == pytest.approx(50 / 125 * 100, abs=0.01)


def test_retention_matrix(cleaned):
    retention = cohort.retention_matrix(cleaned)
    assert (retention[0] == 1).all()
    assert retention.loc[retention.index.astype(str) == "2011-01", 1].iloc[0] == pytest.approx(0.5)
