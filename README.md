# Wealthlab

A local financial scenario workbench for comparing employment, retirement, spending, diversification and conditional investment strategies. It projects actual household cash, taxes, liquidity and account balances, then searches user-bounded policies with spending safety first and after-tax wealth second.

The public repository contains code, public-source references and synthetic examples. Keep household inputs and generated reports in a selected private folder outside the repository. There is no brokerage connection or trading workflow.

## Run locally

From the selected code directory, with Python 3.12 and uv:

```sh
mkdir -p .cache/uv .runtime/tmp
export UV_CACHE_DIR="$PWD/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python"
export TMPDIR="$PWD/.runtime/tmp"
uv sync --frozen --no-dev --extra benchmarks
uv run --no-sync python -m wealthlab serve
```

Open `http://127.0.0.1:8501`. The launcher binds to loopback and disables usage statistics. Stop with Control-C. The recommended installation includes Owl's production retirement tables; a core-only installation blocks applicable Social Security/RMD cases. Intel Mac build prerequisites are in [development setup](docs/development.md).

Start in **Household** with the labelled synthetic example, select **Validate and project**, and keep a comparison baseline. Edit a clone to compare income, spending or retirement assumptions. The simple starter omits taxes; enable an applicable tax plan before interpreting after-tax outcomes. The [local user guide](docs/local-user-guide.md) covers private saves, imports, exports and reproducible CLI runs.

## Workspaces

| Workspace | What you can compare |
|---|---|
| Household | Editable income and spending, employment/vesting, accounts, mortgage/property, tax cash, advisory fees and baseline scenarios. |
| Annual tax / Cross-border | Federal/NJ assessments, dated residence and tax payments, conditional Puerto Rico/Spain profiles, foreign credits and original-return refunds. |
| Tax lots | Actual shares and basis, specific/FIFO/HIFO sales, concentration, harvesting and wash-sale assumptions. |
| Retirement | Traditional/Roth accounts, contributions, conversions, withdrawals, HSA, 529, Social Security, Medicare and required distributions. |
| Markets | Deterministic assumptions, historical replay, correlated Monte Carlo and named stresses, using matched paths for comparisons. |
| Products | Conditional long/short and private funds, exchange funds, covered calls/collars/synthetic exposure, QOZ, drilling and whole life. Supplied contractual and tax terms remain explicit. |
| Optimize | Finite user-set choices and locks for retirement, sales, harvesting, conversions, withdrawal/funding order, contributions, guardrails and supported product allocations. |
| Engine checks | Independent synthetic numerical checks and optional Owl retirement comparison. |

The optimizer defaults to a configurable 95% simulated funding-success target, younger-member age 100 horizon and two-year liquid reserve. It separates training from validation and reports unmet constraints, paid taxes, downside and completed exits. A best evaluated policy is not a global optimum or a validated probability of future success.

Read the [model coverage matrix](docs/model-coverage.md) and [private input checklist](docs/private-input-checklist.md) before entering personal data. Unsupported tax profiles, absent terms and incomplete exits are explicit; a deduction or assessed credit does not become spendable cash. Search also accepts fixed native home/debt and bounded PR/Spain contexts. Relocation, unsupported foreign source mappings and property decisions are not automatic search choices. See [executed workflow checks](docs/release-validation.md) and [release acceptance](https://github.com/pavelkrotkov/wealthlab/issues/19).

## Development and sources

[Confirmed scope](CONTEXT.md) · [Implementation plan](docs/implementation-plan.md) · [Software reuse research](docs/software-research.md) · [Executed reference checks](docs/reuse-results.md) · [Dependency/license notices](docs/dependency-notices.md) · [Development and review](docs/development.md) · [Test audit](docs/test-audit.md)

CI enforces lint, formatting, typing, tests/coverage, dependency and workflow checks, plus CC ≤ 8, MI ≥ 50, module SLOC ≤ 300 and function span ≤ 60. Tests and tooling are included. PRs require independent ChatGPT-Sol 6.1 review at their current commit; J-Bot is on the authorized quota hold.

Original work is GPL-3.0-or-later; see [LICENSE](LICENSE). Dependencies retain their own licenses.
