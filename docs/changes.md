# Changes

## 2026-02-08

- Summary: Added repository quality gate and CI workflow.
- Affected files: `scripts/gate.sh`, `.github/workflows/gate.yml`, `README.md`, `tests/test_parse_item.py`.
- Migration notes: None.
- Validation status: Local gate executed.

## 2026-02-08

- Summary: Stopped versioning generated scrape output and added a sanitized sample dataset.
- Affected files: `.gitignore`, `README.md`, `sample_listings.csv`.
- Migration notes: `all_listings.csv` remains local and is no longer tracked by git.
- Validation status: Local gate executed.
