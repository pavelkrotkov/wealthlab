# ADR 0024: Realized market batches precede household policy simulation

Status: first path-generation/UI layer of market ticket #8. Household lot integration, spending success, confidence intervals, rebalancing, guardrails and linked employment stresses remain unfinished. This layer does not close #8 or retirement #6.

## Reuse and model units

Use the existing pinned NumPy dependency, with no additional financial library. Asset assumptions supply decimal annual arithmetic expected mark return, annual log-return volatility and separate annual cash yield. The correlation matrix follows asset order with inflation last; it must be finite, symmetric, have a unit diagonal and be positive semidefinite. Roundoff tolerance is 1e-12; there is no nearest-correlation repair or inferred replacement matrix.

For deterministic marks, monthly growth is `(1 + annual_mean) ** (1/12) - 1`. Monte Carlo samples joint monthly log shocks using NumPy `Generator(PCG64(seed)).multivariate_normal`, covariance `correlation * outer(volatility, volatility) / 12`, and mean `log1p(annual_mean)/12 - volatility**2/24`. Thus one year's expected mark growth is the specified arithmetic annual expectation under this independent-month lognormal model. Inflation is a correlated factor using the same convention. This is an explicit model with no fat tails, fitted regimes or claim of calibrated future probabilities.

Cash yields are supplied separately, as annual yield divided by twelve or actual historical monthly observations. A price-plus-cash convention cannot silently become a reinvested total-return convention. Reinvested total-return marks require zero separate yield both in assumptions and historical observations. No ex-dividend entitlement, tax character, reinvestment trade or manager return is inferred here.

## History, stresses and reproducibility

Historical replay requires a supplied source, retrieval date, availability cutoff and synthetic/real designation. Observations cover consecutive complete calendar months with all asset marks, cash yields and inflation, exactly matching the requested horizon. The availability cutoff follows the final completed observation; retrieval follows that cutoff and precedes projection start. Missing months, missing factors, duplicate dates and future data block the case. No filling, cycling or favorable-window selection is performed. Supplied provenance is not certification of point-in-time vendor vintage. The bundled historical example is invented mathematical data, visibly labeled as such; no actual market dataset is bundled.

Named stress events multiply specific monthly mark-growth factors, optionally override that month's inflation and lock specified assets for a supplied number of months. Locks preserve marks and have no invented liquidation proceeds. Synthetic templates cover an early crash, three-year inflation regime, loss of the first listed equity/employer factor and noncash illiquidity. Their magnitudes and durations are assumptions, not estimated event probabilities. Stress can overlay deterministic or seeded Monte Carlo paths; the stochastic baseline retains all unshocked observations exactly. Margin calls and actual employment/compensation reactions still require later adapters.

Generate once and reuse the realized batch for all compared policies. Arrays are read-only against accidental writes. Export includes all observations and reproduction metadata, input assumptions, algorithm, NumPy version, seed and a content fingerprint. Pinned numerical dependencies support repeatability; different platforms/linear-algebra versions may produce different floating-point realizations, so the exported batch is the pairing authority rather than a promise of cross-platform bit identity. Local runs are bounded to 1,200 months and two million factor observations to avoid accidental unbounded allocations.

## UI and diagnostic limits

The Markets workspace provides editable/imported JSON for each mode and exports both assumptions and realized paths. Charts show factor mark indices and model percentiles. Separate cash yields accumulate without interest; real buy-and-hold diagnostics include that cash and the simulated inflation index. Mark drawdown is a factor diagnostic, not household portfolio drawdown. These outputs omit household withdrawals, fees, taxes and policy decisions. They cannot establish retirement funding success, usable tax losses or spendable terminal wealth. Household integration must replace proportional-basis selling for any linked lot account and prevent a second adapter from selling the same assets.

## Primary technical references and checks

Checked October 24, 2026: [NumPy multivariate-normal documentation](https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.multivariate_normal.html) specifies joint sampling, positive-semidefinite covariance, explicit invalid-matrix behavior and factorization choices. [NumPy random stream guidance](https://numpy.org/doc/stable/reference/random/parallel.html) explains repeatable seeded streams; this implementation uses one explicit PCG64 generator per generated batch and no candidate-specific resampling.

Checks independently verify deterministic compounding, separate cash without reinvestment, one-year Monte Carlo expectation, observed joint log correlation, zero-volatility equivalence, seed repeatability, complete past history, return-stream nonduplication, matrix/resource guards, paired stress preservation, inflation compounding, retained locked value, total-loss persistence and all four real Streamlit form paths.
