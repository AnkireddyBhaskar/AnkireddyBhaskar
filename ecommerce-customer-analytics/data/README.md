# Data

The raw dataset is **not committed** to the repository. It is downloaded automatically from the
[UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/352/online+retail) the first time
the pipeline or notebook runs, and cached here as `online_retail.csv`.

You can also download it manually:

```bash
python -c "from retail_analysis.data import download_dataset; download_dataset()"
```

(run from the `src/` directory, or with `PYTHONPATH=src`).

**Citation:** Chen, D. (2015). *Online Retail* [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5BW33. Licensed under CC BY 4.0.

| Column | Description |
|---|---|
| `InvoiceNo` | 6-digit invoice number; a leading `C` marks a cancellation |
| `StockCode` | 5-digit product code |
| `Description` | Product name |
| `Quantity` | Units per line item |
| `InvoiceDate` | Invoice date and time |
| `UnitPrice` | Price per unit in GBP (£) |
| `CustomerID` | 5-digit customer identifier |
| `Country` | Customer's country of residence |
