# Wealthlab

A local-first financial scenario workbench. **Early implementation: household editing, monthly cash-flow comparison, a separate annual federal/NJ tax workbench and engine checks run locally. Optional household tax cash flows and permitted taxable-account funding now run. State-tax payment deductions and conditional refund recognition are included. The Tax lots page adds lot accounting, optional federal/NJ wash scenarios, dated retain/sell/staged/concentration/tax-budget policies and conditional annual liability comparisons; matched long-only harvesting comparisons and a hypothetical taxable-account exit. Dated recurring fees distinguish paid/owed cash charges from embedded-price estimates. Distribution entitlements, receipts and conditional dividend qualification feed annual tax comparisons. Current-loss attribution separates own/external gain use, ordinary consumption and carry from actual liability differences. The Retirement workspace adds dated 2025/2026 IRA and employee 401(k) contribution allocation, cash shortfalls and separate federal/NJ basis additions. The retirement workbench includes conditional IRA withdrawals/conversions, basis reconciliation, Roth clocks and required-withdrawal targets. The HSA cash layer adds monthly family/Medicare limits and shared medical-receipt tracking; its annual tax and household integration remain unfinished. The Education layer adds savings-type 529 funding, explicit higher-education expense allocation, separate tax recipients and conditional NJBEST history; household integration remains unfinished. The Medicare layer adds explicit income lookback, conditional future premiums and dated cash shortfalls; Social Security and household benefit integration remain unfinished. Benefits, household lot integration, special distributions, market paths, product strategies and optimization remain in progress.**

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

Open the localhost address printed by Streamlit. The Household page starts with an explicitly synthetic example; edit the tables and select **Validate and project**. Keep a baseline to compare a clone. The Annual tax page edits standalone federal/NJ cases. Enable Household tax assumptions in the household form to include annual recognition, withholding, estimated payments, December settlement, delayed refunds and optional permitted taxable-account sales. The editable starter assumes wages and frozen 2025 law; review its mappings and annual cases. See [tax cash-flow conventions](docs/adr/0003-tax-cash-flow.md). See [tax coverage and limits](docs/tax-rules.md). The Tax lots page provides dated trade accounting, FIFO/HIFO/specific selection, separate bases and an optional sale-decision form with explicit current prices; choose the **Harvesting comparison** synthetic example to compare holding and exit outcomes. [Its documented scope](docs/adr/0004-lots-and-harvesting.md) distinguishes conditional annual tax savings from household cash benefits. The Retirement page starts with a synthetic high-earner case and shows requested versus funded contributions, deductions and basis. [Contribution coverage](docs/adr/0005-retirement.md) and [IRA withdrawal coverage](docs/adr/0006-ira-withdrawals.md) list supported rules and unfinished layers. Switch the Retirement workbench to IRA withdrawals for dated cash, basis and conditional annual tax results, HSA for [cash funding and receipt checks](docs/adr/0007-hsa.md), Education for [529 funding and annual expense allocation](docs/adr/0008-education.md), or Medicare for [IRMAA history and premium funding](docs/adr/0009-medicare.md). The Engine checks page runs independent numerical cases. See [cash-flow conventions](docs/adr/0002-household-cash-flow.md) for current limits. The optional `benchmarks` extra adds Owl and its solver dependencies. See [development setup](docs/development.md) for cache locations and Intel-Mac build prerequisites, and [executed reuse checks](docs/reuse-results.md) for what has actually been validated.

Original work is GPL-3.0-or-later; see [LICENSE](LICENSE). Third-party dependencies retain their own licenses.
