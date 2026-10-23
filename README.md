# Wealthlab

A local-first financial scenario workbench. **Early implementation: household editing, monthly cash-flow comparison and engine checks run locally. Household taxes, market paths, product strategies and optimization are still being implemented.**

The intended workflow is to define a household, compare explicit policies under the same market paths, inspect spending shortfalls and taxes, and explore better policies within user-set bounds.

- [Scope and glossary](CONTEXT.md)
- [Software reuse research](docs/software-research.md)
- [Implementation tickets, dependencies and acceptance checks](docs/implementation-plan.md)
- [Architecture decisions](docs/adr/0001-local-scenario-workbench.md)

The public repository contains code, public-source references and synthetic fixtures only. Household records, account exports, credentials and private illustrations stay outside version control. No brokerage trading or account connection is planned for the first complete version.

## Delivery standard

Every feature must work through the UI and calculation engine, expose its assumptions, include a reproducible check, and pass code quality and review. An unsupported tax rule or missing product term must be visible; it must not silently become a zero tax rate or guaranteed return.

## Run locally

```sh
mkdir -p .cache/uv .runtime/tmp
export UV_CACHE_DIR="$PWD/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python"
export TMPDIR="$PWD/.runtime/tmp"
uv sync --frozen --dev --extra benchmarks
uv run --frozen --extra benchmarks streamlit run app.py
```

Open the localhost address printed by Streamlit. The Household page starts with an explicitly synthetic example; edit the tables and select **Validate and project**. Keep a baseline to compare a clone. The Engine checks page runs independent numerical cases. See [cash-flow conventions](docs/adr/0002-household-cash-flow.md) for current limits. The optional `benchmarks` extra adds Owl and its solver dependencies. See [development setup](docs/development.md) for cache locations and Intel-Mac build prerequisites, and [executed reuse checks](docs/reuse-results.md) for what has actually been validated.

Original work is GPL-3.0-or-later; see [LICENSE](LICENSE). Third-party dependencies retain their own licenses.
