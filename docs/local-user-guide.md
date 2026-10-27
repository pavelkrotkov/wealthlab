# Local workbench guide

Release integration is still open in [issue #19](https://github.com/pavelkrotkov/wealthlab/issues/19). This guide covers the current main-based workbench and the local launch/report changes in this layer. Read the [coverage matrix](model-coverage.md) before entering a case; pending product, jurisdiction and optimizer branches are not a completed integrated release.

## Install and launch on the selected Mac

Use the selected Wealthlab code folder and Python 3.12. Keep build artifacts there:

```sh
mkdir -p .cache/uv .runtime/tmp
export UV_CACHE_DIR="$PWD/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python"
export TMPDIR="$PWD/.runtime/tmp"
uv sync --frozen --no-dev --extra benchmarks
uv run --no-sync python -m wealthlab serve
```

Run these commands from the selected repository. Open `http://127.0.0.1:8501`. The launcher always selects that repository's app, binds to loopback, disables usage statistics and limits uploads. `--port 8502` selects another local port. Stop with Control-C. It does not open a public server or connect brokerage accounts.

Intel macOS builds may need the existing LLVM 22 prerequisites described in [development setup](development.md). The recommended full install includes the existing `benchmarks` extra because Owl also supplies production FRA/RMD tables; it is not merely a benchmark dependency. Follow the existing Cargo/OpenSSL prerequisites in development setup on this Intel Mac. A deliberately limited core-only install (`uv sync --frozen --no-dev`) can launch cash-flow screens but blocks applicable Social Security/RMD cases and shows that limitation before running. Add `--dev` when you also need the repository's development checks.

## Start with synthetic data

1. Open **Household** and keep the clearly labelled synthetic example. Select **Validate and project**. The starter omits taxes and is not an after-tax retirement plan.
2. Keep it as the comparison baseline. Edit a clone's spending or retirement date and project again. Different projection dates block comparison.
3. Inspect nominal/real wealth, required-payment shortfalls, liquid reserves, tax positions and the detailed account/product audits. An optional unfilled request differs from required-payment failure.
4. Use the named synthetic loaders and the Annual tax, Tax lots, Retirement, Markets and Products workspaces within their stated supported scopes. Each workbench retains its own assumptions and warnings.
5. Export the projection's inputs/full ledger/reproduction details. The export retains the source revision/dirty flag, dependency versions, input fingerprint and actual monthly audit rows. It can contain private data after you replace synthetic inputs.

A report records conditional calculations, not a full-tax optimization certificate. Continued marks, actual liquidation and spendable wealth are different outputs. Unsupported legal, product or quote assumptions must remain blocked or explicitly conditional.

## Save, import and reproduce locally

Choose an **existing private directory** outside every checkout of this public code repository. The app does not invent or create a private destination. Household / Save a private scenario writes a raw validated scenario atomically to a new `.json` name. Existing files and destination symlinks cannot be overwritten. Use a new name for another version. The selected filesystem must support the exclusive hard-link save operation; a failed save leaves existing files intact.

Household / Load scenario JSON accepts a raw scenario or a projection report produced by this version. Report import validates its embedded inputs and fingerprint, discards archived outcomes, and requires a fresh projection. It never trusts an old balance as a current fact. UTF-8/BOM input is supported with a 2,000,000-byte bound; oversized or invalid files are rejected. Raw scenario saves remain available when a full audit report exceeds that import bound.

Browser downloads follow the browser's save controls; choose your private destination. Do not place real inputs, reports or screenshots in this public repository, GitHub issues/reviews or shared logs. The app's calculation path does not upload scenarios. Clicking an external documentation/source link is a separate user action.

For the same calculation without a browser:

```sh
uv run --no-sync python -m wealthlab project examples/synthetic.json
uv run --no-sync python -m wealthlab project "/your/selected/private/folder/scenario.json" --output-directory "/your/selected/private/folder" --filename projection.json
uv run --no-sync python -m wealthlab compare "/your/selected/private/folder/baseline.json" "/your/selected/private/folder/candidate.json" --output-directory "/your/selected/private/folder" --filename comparison.json
```

Without `--output-directory`, project/compare deliberately write their full JSON report to the local terminal. That output can be private; keep it out of shared logs. Supplying a filename requires a selected directory. CLI errors omit raw scenario values and private input paths. A blocked or invalid action returns nonzero and writes no report.

To reproduce, import a saved raw scenario or projection report and project again, or pass either to the CLI. Check the recorded input fingerprint, clean source revision and dependency versions; a dirty checkout or missing revision cannot establish exact reproducibility. Re-execution uses the current engine and does not certify that a different version's archived result is identical. The dependency record includes the installed Owl version, or explicit `null` when its retirement tables are absent; it does not substitute the version expected by the lock file. The UI and CLI share the actual household engine and report format; CLI comparison requires aligned dates and does not run the still-in-progress personal optimizer.

## Before private entry

Use the [private input checklist](private-input-checklist.md). Confirm ownership, units, basis, cash versus taxable allocations, dates, legal assumptions and completeness independently. Leave unknown critical facts unresolved. Do not supply credentials: there is no account-connection workflow. A successful synthetic run is not evidence that your own eligibility, product terms or retirement safety are established.
