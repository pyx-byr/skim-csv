# skim-csv

> Fast CLI tool for profiling and summarizing large CSV files without loading them fully into memory.

---

## Installation

```bash
pip install skim-csv
```

Or install from source:

```bash
git clone https://github.com/yourname/skim-csv.git && cd skim-csv && pip install .
```

---

## Usage

```bash
skim path/to/file.csv
```

**Example output:**

```
File: sales_data.csv  |  Rows: 1,482,301  |  Columns: 12

Column            Type       Non-Null    Unique     Min         Max         Mean
----------------  ---------  ----------  ---------  ----------  ----------  -------
order_id          integer    100.0%      1,482,301  1           1482301     —
revenue           float      98.3%       84,201     0.99        14,999.00   127.43
region            string     99.1%       8          —           —           —
order_date        datetime   100.0%      730        2022-01-01  2023-12-31  —
```

**Options:**

| Flag              | Description                          |
|-------------------|--------------------------------------|
| `--delimiter`     | Specify CSV delimiter (default: `,`) |
| `--encoding`      | File encoding (default: `utf-8`)     |
| `--sample N`      | Profile only first N rows            |
| `--output json`   | Export summary as JSON               |

```bash
# Sample first 100,000 rows and export to JSON
skim large_file.csv --sample 100000 --output json > summary.json
```

---

## Why skim-csv?

- **Streaming** — processes files row-by-row, never loads everything into RAM
- **Fast** — handles multi-GB files in seconds
- **Zero heavy dependencies** — no pandas required

---

## License

MIT © 2024 [yourname](https://github.com/yourname)