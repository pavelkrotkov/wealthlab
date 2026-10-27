# Development and review

The household, tax, retirement, market and product workbenches have implemented conditional slices; see the [current coverage matrix](model-coverage.md). Optimizer, jurisdiction and complete release integration remain active work. The [local user guide](local-user-guide.md) recommends the complete installation, including the pinned Owl tables used by SSA/RMD calculations. The environment below also includes development checks; core-only installation is explicitly limited.

Use Python 3.12 and uv. Keep local build/cache/temp artifacts inside the selected repository:

```sh
mkdir -p .cache/uv .runtime/tmp
export UV_CACHE_DIR="$PWD/.cache/uv"
export UV_PYTHON_INSTALL_DIR="$PWD/.runtime/python"
export TMPDIR="$PWD/.runtime/tmp"
uv sync --frozen --dev --extra benchmarks
uv run --no-sync ruff check .
uv run --no-sync ruff format --check .
uv run --no-sync ty check .
uv run --no-sync python -m tools.quality
uv run --no-sync pytest --cov --cov-report=term-missing --basetemp=.runtime/pytest
uv run --no-sync pip-audit --cache-dir=.cache/pip-audit
uv run --no-sync zizmor .github/workflows
```

The metrics command inspects all tracked and unignored Python files, including root UI modules, tests and tools. Only git-ignored environments/generated/private material is outside discovery. It reports each file and fails on CC > 8, MI < 50, source lines > 300 or function span > 60. Deliberately bad synthetic cases verify rejection. Coverage starts at 85% and its source list must expand with production packages.

## Independent PR review

As authorized on October 26, 2026, the active reviewer is ChatGPT-Sol 6.1 (`gpt-6.1-sol`), replacing J-Bot while its weekly quota is exhausted. Run the reviewer as an independent Codex subagent with that explicit model; this uses the existing agent runtime, not the CommandCode-backed GitHub Action. The reviewer must not implement its own fixes or merge its target.

Freeze the full PR head SHA and inspect its merge-base diff, requirements, relevant callers and tests. Reviewers may work in parallel on separate PRs. Publish worthwhile findings with evidence and requested handling. After the findings are visible, submit a native GitHub PR review with `event=COMMENT` and `commit_id` set to the reviewed SHA. Include model identity, verdict, finding count and marker `<!-- wealthlab-review:sol-6.1:PR_NUMBER:FULL_HEAD_SHA -->`. A COMMENT review records evidence; it does not confer an APPROVED state or bypass GitHub branch protection.

Before publishing, re-read the PR head and abort if it changed. Check existing native reviews for the exact marker to avoid duplicates. After publication, re-read the native review and require the matching commit, submitted COMMENTED state, submission timestamp and consistent finding count; recheck that the PR head is unchanged. Errors, incomplete reviews, local reports and reviews of previous heads do not satisfy the review gate. Address findings, rerun affected checks and obtain review of the new head after fixes. Merge only after required CI passes and all findings have been resolved.

The existing J-Bot workflow remains available for a future explicitly authorized return: write-authorized `/jbot --model=provider/model` comments freeze the same-repository PR head. Do not trigger it during the quota hold. Provider credentials remain in GitHub Actions secrets; this reviewer change requires no new secret, model-provider subscription or paid quota override.

The public examples and CI must never load local household records. Streamlit is configured to listen only on loopback with usage statistics disabled. The future app must preserve these settings and test imports/exports and input trust boundaries.

## Numerical package setup on Intel macOS

Tax-Calculator 6.8.5 pins Numba 0.67.0 / llvmlite 0.49.0. This Intel Mac requires their source builds. The existing MacPorts LLVM 22 toolchain was sufficient; no system installation was performed. Before the first sync on this configured machine:

```sh
export LLVM_DIR=/opt/local/libexec/llvm-22/lib/cmake/llvm
export CMAKE_PREFIX_PATH=/opt/local/libexec/llvm-22
```

Other machines need a compatible prebuilt dependency wheel or LLVM toolchain; do not silently downgrade tax law to solve packaging. The required-environment list includes Intel macOS and Linux. Owl's optional extra pins the tested 2026.10.10 release and patched cryptography >= 50; the resolver selects a compatible MOSEK distribution although the benchmark uses the free HiGHS solver. Dependency audits include the optional environment in CI. `uv run --no-sync` preserves the environment selected by the preceding sync.

On Intel macOS, cryptography 50.0.2 was built with the existing Rust 1.99.1 and OpenSSL 3, plus the official Cargo 1.99.0 component downloaded and SHA-256-verified inside `.runtime/toolchain`. Set `CARGO_HOME` to `.cache/cargo`, add that component's `cargo/bin` to PATH, and set `OPENSSL_DIR=/opt/local/libexec/openssl3` before syncing the optional benchmark. Do not pin a vulnerable older cryptography to avoid a build. Core operation does not require the benchmark extra.

`wealthlab.runtime.configure()` sets numerical/font/cache/temp paths under this repository before imports. Tests use the same setup. CI runs the optional Owl benchmark as well as the core checks; a default installation without the extra skips only that explicitly optional check.
