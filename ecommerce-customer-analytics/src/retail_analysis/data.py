"""Loading and cleaning the UCI Online Retail dataset."""

from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path

import pandas as pd

DATASET_URL = "https://archive.ics.uci.edu/static/public/352/online+retail.zip"
DATA_DIR = Path(__file__).resolve().parents[2] / "data"
RAW_CSV = DATA_DIR / "online_retail.csv"

NON_PRODUCT_CODES = {"POST", "D", "M", "C2", "DOT", "BANK CHARGES", "PADS", "AMAZONFEE", "CRUK", "S", "B"}


def download_dataset(dest: Path = RAW_CSV) -> Path:
    """Download the dataset from the UCI repository and cache it as CSV."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(DATASET_URL) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    with archive.open("Online Retail.xlsx") as xlsx:
        df = pd.read_excel(xlsx, dtype={"InvoiceNo": str, "StockCode": str})
    df.to_csv(dest, index=False)
    return dest


def load_raw(path: Path = RAW_CSV) -> pd.DataFrame:
    """Load the raw transactions, downloading them first if needed."""
    if not path.exists():
        download_dataset(path)
    return pd.read_csv(
        path,
        dtype={"InvoiceNo": str, "StockCode": str, "CustomerID": "Int64"},
        parse_dates=["InvoiceDate"],
    )


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Return a cleaned transaction table ready for analysis.

    Steps:
      * drop exact duplicate rows
      * drop cancellations (invoice numbers starting with ``C``) together with the
        original order lines they reverse (same customer, product and quantity)
      * drop rows with non-positive quantity or price
      * drop non-product line items (postage, manual adjustments, fees)
      * add ``Revenue`` and calendar helper columns
    """
    out = df.drop_duplicates().copy()
    out["InvoiceNo"] = out["InvoiceNo"].astype(str)
    out["StockCode"] = out["StockCode"].astype(str).str.upper()
    out["Description"] = out["Description"].astype("string").str.strip()

    is_cancel = out["InvoiceNo"].str.startswith("C")
    out = _drop_reversed_orders(out[~is_cancel], out[is_cancel])
    out = out[(out["Quantity"] > 0) & (out["UnitPrice"] > 0)]
    out = out[~out["StockCode"].isin(NON_PRODUCT_CODES)]

    out["Revenue"] = out["Quantity"] * out["UnitPrice"]
    out["InvoiceMonth"] = out["InvoiceDate"].dt.to_period("M")
    out["Weekday"] = out["InvoiceDate"].dt.day_name()
    out["Hour"] = out["InvoiceDate"].dt.hour
    return out.reset_index(drop=True)


def _drop_reversed_orders(orders: pd.DataFrame, cancellations: pd.DataFrame) -> pd.DataFrame:
    """Remove the most recent order lines that are fully reversed by a cancellation."""
    key = ["CustomerID", "StockCode", "AbsQuantity"]
    cancels = cancellations.assign(AbsQuantity=cancellations["Quantity"].abs()).dropna(subset=["CustomerID"])
    cancel_counts = cancels.groupby(key).size().rename("n_cancelled")
    candidates = orders.assign(AbsQuantity=orders["Quantity"]).sort_values("InvoiceDate", ascending=False)
    candidates["rank"] = candidates.groupby(key, dropna=False).cumcount()
    candidates = candidates.join(cancel_counts, on=key)
    reversed_mask = candidates["rank"] < candidates["n_cancelled"].fillna(0)
    return orders.drop(index=candidates.index[reversed_mask])


def cleaning_report(raw: pd.DataFrame, cleaned: pd.DataFrame) -> pd.Series:
    """Summarise how much data the cleaning step removed."""
    return pd.Series(
        {
            "raw_rows": len(raw),
            "duplicate_rows": int(raw.duplicated().sum()),
            "cancelled_rows": int(raw["InvoiceNo"].astype(str).str.startswith("C").sum()),
            "missing_customer_id": int(raw["CustomerID"].isna().sum()),
            "clean_rows": len(cleaned),
            "rows_removed_pct": round(100 * (1 - len(cleaned) / len(raw)), 2),
        }
    )
