# Development and review

The application is not yet implemented. This layer establishes executable quality gates.

Use Python 3.12 and uv. Keep local build/cache/temp artifacts inside the selected repository:

```sh
mkdir -p .cache/uv .runtime/tmp
export UV_CACHE_DIR="$PWD/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python"
export TMPDIR="$PWD/.runtime/tmp"
uv sync --frozen --dev
uv run --frozen ruff check .
uv run --frozen ruff format --check .
uv run --frozen ty check .
uv run --frozen python -m tools.quality
uv run --frozen pytest --cov --cov-report=term-missing --basetemp=.runtime/pytest
uv run --frozen pip-audit
uv run --frozen zizmor .github/workflows
```

The metrics command inspects all tracked and unignored Python files, including root UI modules, tests and tools. Only git-ignored environments/generated/private material is outside discovery. It reports each file and fails on CC > 8, MI < 50, source lines > 300 or function span > 60. Deliberately bad synthetic cases verify rejection. Coverage starts at 85% and its source list must expand with production packages.

J-Bot follows utils: write-authorized `/jbot --model=provider/model` comments freeze the same-repository PR head. Provider credentials belong in GitHub Actions secrets. Use the repo's configured provider and observe the review on the current SHA; errors or missing credentials never count as a review. The workflow must first exist on the default branch for issue-comment events; seed that trusted workflow as documented bootstrap before enforcing review requirements on feature work.

The public examples and CI must never load local household records. Streamlit is configured to listen only on loopback with usage statistics disabled. The future app must preserve these settings and test imports/exports and input trust boundaries.
