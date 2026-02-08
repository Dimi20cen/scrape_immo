#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

run_lint() {
  echo "[lint] Checking Python syntax"
  python -m py_compile immoscout_bulk_scraper.py
}

run_typecheck() {
  echo "[typecheck] Running fallback static check"
  python - <<'PY'
from pathlib import Path
import ast

source = Path("immoscout_bulk_scraper.py").read_text(encoding="utf-8")
ast.parse(source)
print("AST parse check passed")
PY
}

run_test() {
  echo "[test] Running unit tests"
  python -m unittest discover -s tests -p "test_*.py" -v
}

run_docs() {
  echo "[docs] Verifying required docs"
  test -f README.md
  test -f docs/changes.md
}

main() {
  run_lint
  run_typecheck
  run_test
  run_docs
  echo "[gate] All checks passed"
}

main "$@"
