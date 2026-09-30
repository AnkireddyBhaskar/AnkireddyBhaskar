import pandas as pd
import pytest


@pytest.fixture
def raw_transactions() -> pd.DataFrame:
    rows = [
        # InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country
        ("1001", "A1", "MUG", 2, "2011-01-05 10:00", 5.0, 1, "United Kingdom"),
        ("1001", "B2", "PLATE", 1, "2011-01-05 10:00", 10.0, 1, "United Kingdom"),
        ("1001", "B2", "PLATE", 1, "2011-01-05 10:00", 10.0, 1, "United Kingdom"),  # duplicate
        ("1002", "A1", "MUG", 4, "2011-02-10 12:00", 5.0, 1, "United Kingdom"),
        ("1003", "A1", "MUG", 1, "2011-01-20 09:00", 5.0, 2, "France"),
        ("1003", "B2", "PLATE", 3, "2011-01-20 09:00", 10.0, 2, "France"),
        ("C1004", "A1", "MUG", -2, "2011-01-21 09:00", 5.0, 2, "France"),  # unmatched cancellation
        ("1005", "POST", "POSTAGE", 1, "2011-01-22 09:00", 18.0, 2, "France"),  # non-product
        ("1006", "C3", "LAMP", 1, "2011-03-01 15:00", 0.0, 3, "Germany"),  # zero price
        ("1007", "C3", "LAMP", 2, "2011-03-02 15:00", 25.0, 3, "Germany"),
        ("1008", "A1", "MUG", 1, "2011-03-03 16:00", 5.0, None, "Germany"),  # guest checkout
        ("1009", "D4", "BIRDIE", 500, "2011-03-04 09:00", 2.0, 3, "Germany"),  # reversed by C1010
        ("C1010", "D4", "BIRDIE", -500, "2011-03-04 09:05", 2.0, 3, "Germany"),
    ]
    df = pd.DataFrame(
        rows,
        columns=["InvoiceNo", "StockCode", "Description", "Quantity", "InvoiceDate", "UnitPrice", "CustomerID", "Country"],
    )
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["CustomerID"] = df["CustomerID"].astype("Int64")
    return df
