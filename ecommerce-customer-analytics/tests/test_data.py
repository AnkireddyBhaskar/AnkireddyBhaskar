from retail_analysis import data


def test_clean_removes_bad_rows(raw_transactions):
    cleaned = data.clean(raw_transactions)
    assert len(cleaned) == 7
    assert not cleaned["InvoiceNo"].str.startswith("C").any()
    assert (cleaned["Quantity"] > 0).all()
    assert (cleaned["UnitPrice"] > 0).all()
    assert "POST" not in set(cleaned["StockCode"])
    assert "1009" not in set(cleaned["InvoiceNo"])


def test_clean_adds_revenue_and_calendar_columns(raw_transactions):
    cleaned = data.clean(raw_transactions)
    assert (cleaned["Revenue"] == cleaned["Quantity"] * cleaned["UnitPrice"]).all()
    assert {"InvoiceMonth", "Weekday", "Hour"} <= set(cleaned.columns)


def test_cleaning_report(raw_transactions):
    report = data.cleaning_report(raw_transactions, data.clean(raw_transactions))
    assert report["raw_rows"] == 13
    assert report["duplicate_rows"] == 1
    assert report["cancelled_rows"] == 2
    assert report["missing_customer_id"] == 1
    assert report["clean_rows"] == 7
