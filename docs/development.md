# Development and review

The household cash-flow editor and verification screen are implemented. Tax, market, product and optimization modules remain on the issue backlog.

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

J-Bot follows utils: write-authorized `/jbot --model=provider/model` comments freeze the same-repository PR head. Provider credentials belong in GitHub Actions secrets. Use the repo's configured provider and observe the review on the current SHA; errors or missing credentials never count as a review. The workflow must first exist on the default branch for issue-comment events; seed that trusted workflow as documented bootstrap before enforcing review requirements on feature work.

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
