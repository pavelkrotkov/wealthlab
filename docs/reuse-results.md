# Executed reuse checks

October 23, 2026, local Intel macOS, Python 3.12.15. All data in these checks are independently synthetic. Small checks establish an integration foothold, not correctness for every input or a complete household tax model.

| Component | Installed version | Independent case | Observed result |
|---|---|---|---|
| Tax-Calculator | 6.8.5 | 2025 joint filers both age 40, no dependents, $150,000 wages and standard deduction | Federal income tax $15,898; employee regular payroll $11,475 |
| Tax-Calculator | 6.8.5 | Same filers, $150,000 long-term gains and no wages | Federal income tax $3,270 |
| QuantLib | 1.44 | One-year European ATM call, spot/strike 100, rate 4%, volatility 20%, zero dividends | 9.925053717274428 versus independent 9.925053717274437 |
| Focused NJ spike | 2025 | Joint taxable income $200,000; disposition category loss and netting checks | Tax $8,697.50; losses do not offset wages |
| Owl / HiGHS | 2026.10.10 / 1.15.1 | $120,000 cash, zero returns/inflation, no benefits or healthcare costs, 11 annual periods | $10,909.09 annual spending versus $120,000 / 11 |

The federal benchmark uses the [2025 IRS standard deduction](https://www.irs.gov/publications/p501), [2025 brackets](https://www.irs.gov/filing/federal-income-tax-rates-and-brackets), [capital-gain thresholds](https://www.irs.gov/taxtopics/tc409) and [employee payroll rates](https://www.irs.gov/taxtopics/tc751). Income-tax expected values were calculated independently from these schedules. Tax-Calculator reports employer plus employee regular payroll in `ptax_was`; treating that as household employee cost would double-count the regular payroll burden. The check distinguishes them. This mapping is only for the stated wage case, not self-employment or cross-border social insurance.

Tax-Calculator's default policy horizon ends at 2036 in the installed release. A lifetime model requires explicit future-policy assumptions and validation beyond that horizon. No automatic 50-year extrapolation is implemented here.

Owl's repository reported 2026.10.22, but the latest package resolved locally was 2026.10.10. The executable benchmark uses the installed version and a supported simple case; current repository documentation must not be assumed to describe every installed behavior. Average-cost taxable accounting and lack of TLH still prevent using it as the authoritative concentration-transition ledger. No Owl documentation or reserved artwork was copied.

The [PolicyEngine NJ gross-income source](https://github.com/PolicyEngine/policyengine-us/blob/main/policyengine_us/variables/gov/states/nj/tax/income/adjusted_gross_income/nj_gross_income.py) explicitly nets/clamps separate loss-eligible categories. This is more promising than a flat-rate substitute. The focused alternative passes independent 2025 joint-rate and disposition-category checks using the [official NJ-1040 instructions](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf), printed pages 11–12 and 63. We choose a focused custom NJ ledger to retain jurisdiction-specific basis and explicit household allocation. PolicyEngine itself was source-inspected, not executed; no claim of full coverage is made. The current spike deliberately supports one rate interval and wages/dispositions only; exemptions, exclusions, credits and other categories remain issue #4.

Run the checks from the local verification UI, or `uv run --extra benchmarks pytest tests/test_engine_checks.py tests/test_owl_benchmark.py tests/test_app.py`. The UI preserves measured batch execution time, actual and expected values, an explicit one-cent acceptance tolerance and package versions. The option model is an analytic European benchmark, not an American assignment/margin simulation.

The optional environment initially resolved an older cryptography wheel; its audit failed. The retained lock uses patched cryptography 50.0.2, built locally with a project-local Cargo component. No vulnerability exception was added.
