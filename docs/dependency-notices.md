# Dependency and source notices

Checked October 25, 2026 against `uv.lock`, installed package metadata/licenses and the upstream references below. Original Wealthlab code is GPL-3.0-or-later under [LICENSE](../LICENSE). Dependencies keep their own notices; importing them does not replace their licenses. No package source, Owl documentation/branding, private adviser material or restricted market dataset is copied into this repository by this release layer.

| Direct core dependency | Locked version | License reference |
|---|---|---|
| NumPy | 2.5.4 | [NumPy licensing](https://numpy.org/doc/stable/license.html). Installed SPDX expression: BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0, including bundled components. |
| Pydantic | 2.14.1 | [MIT license](https://github.com/pydantic/pydantic/blob/main/LICENSE). |
| Tax-Calculator | 6.8.5 | [CC0 license](https://github.com/PSLmodels/Tax-Calculator/blob/master/LICENSE). Federal computations do not establish NJ/foreign treatment. |
| QuantLib Python | 1.44 | [Modified BSD / 3-Clause BSD](https://www.quantlib.org/license.shtml). Model pricing does not supply actual contract quotes. |
| Streamlit | 1.66.1 | [Apache-2.0 license](https://github.com/streamlit/streamlit/blob/1.66.1/LICENSE). Local launch disables usage statistics and binds loopback. |

Tax-Calculator's numerical dependencies include Numba 0.67.0 (BSD) and llvmlite 0.49.0 (installed expression BSD-2-Clause AND Apache-2.0 WITH LLVM-exception). Keep their installed license files and bundled-component notices if redistributing an environment. The frozen lock is the full transitive version manifest; this table is a direct-dependency reference, not a substitute for each distribution's license files.

The recommended full installation includes the existing `benchmarks` extra, which currently selects Owl 2026.10.10 ([GPLv3 source](https://github.com/mdlacasse/Owl/blob/main/LICENSE), separately licensed documentation), SciPy 1.18.1 (BSD with bundled-component notices), cryptography 50.0.2 ([Apache-2.0 OR BSD-3-Clause](https://github.com/pyca/cryptography/blob/main/LICENSE)) and HiGHS/highspy 1.15.1 ([MIT](https://github.com/ERGO-Code/HiGHS/blob/master/LICENSE.txt)). The installed optional set also contains MOSEK 10.2.19 under its [separate license agreement](https://www.mosek.com/products/license-agreement/); the tested Owl benchmark uses HiGHS. Owl also supplies production FRA/RMD tables, so a smaller core-only environment is explicitly limited. The independent benchmark uses HiGHS and does not infer a MOSEK license entitlement.

Calculation exports retain the actual core dependency versions and source revision, so a lock/environment mismatch is visible. Public numerical fixtures are original synthetic cases or specifically attributed official examples. Owning ADRs distinguish source facts from conditional classifications and contain the applicable year/jurisdiction references. Review [software reuse research](software-research.md), [executed checks](reuse-results.md) and the [coverage matrix](model-coverage.md) before extending a package beyond its validated scope.
