# csv-diff-cli

A command-line tool to compare two CSV files and output human-readable diffs with column-aware formatting.

---

## Installation

```bash
pip install csv-diff-cli
```

Or install from source:

```bash
git clone https://github.com/yourname/csv-diff-cli.git
cd csv-diff-cli
pip install .
```

---

## Usage

```bash
csv-diff old.csv new.csv
```

**Example output:**

```
~ Row 3  | name: "Alice" → "Alicia"
          | age:  "30"    → "31"

+ Row 7  | name: "Bob" | age: "25" | city: "Austin"

- Row 9  | name: "Carol" | age: "28" | city: "Denver"
```

**Options:**

| Flag | Description |
|------|-------------|
| `--key COLUMN` | Use a column as a unique row identifier |
| `--ignore COLUMN` | Exclude a column from comparison |
| `--output FORMAT` | Output format: `text` (default), `json`, or `csv` |
| `--no-color` | Disable colored terminal output |

```bash
# Compare using 'id' as the row key, ignore 'updated_at'
csv-diff old.csv new.csv --key id --ignore updated_at
```

---

## Requirements

- Python 3.8+
- No external dependencies (standard library only)

---

## Contributing

Pull requests are welcome. Please open an issue first to discuss any significant changes.

---

## License

This project is licensed under the [MIT License](LICENSE).