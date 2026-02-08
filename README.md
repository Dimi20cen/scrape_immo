# scrape_immo

Bulk scraper for Swiss rental listings on immoscout24.ch.

## Requirements

- Python 3.10+
- Chrome/Chromium installed locally
- `undetected-chromedriver` for runtime scraping

## Usage

```bash
python immoscout_bulk_scraper.py
```

The script writes results to `all_listings.csv`.

## Quality Gate

Run the local gate:

```bash
bash scripts/gate.sh
```

The gate runs:

- `lint`: Python syntax check (`py_compile`)
- `typecheck`: AST parse check (fallback static check)
- `test`: unit tests under `tests/`
- `docs`: verifies required docs files exist
