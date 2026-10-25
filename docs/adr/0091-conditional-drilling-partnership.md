# ADR 0091: Conditional drilling partnership cash and household tax

Status: synthetic vertical slice for #13, dependent on [independent partnership tax facts](0090-supplied-partnership-tax-facts.md). No dependency added.

## Source and legal scope

Products / Drilling partnerships edits the complete household and monthly contract in JSON. Original base, poor-production, denied, deferred and creditor-claim examples are available. These are supplied cash-basis, debt-free property illustrations, not sponsor terms or eligibility findings. GP/LP, working-interest status, applicable liability exposure and SE classification are explicit independent assumptions. Unknown choices and unconfirmed recognition/limit/history facts block computation. A modeled nonrecourse assumption never establishes a legal liability cap; unmodeled liabilities remain explicitly unresolved.

Primary authorities checked October 25, 2026: [2025 Publication 925](https://www.irs.gov/publications/p925) separates partnership basis, at-risk and passive limitations and describes the oil/gas working-interest exception's liability conditions. Its working-interest and ordering passages were also discovered/read through the existing local tax-reference collection. [2025 K-1 instructions](https://www.irs.gov/instructions/i1065sk1) separately report box-14 earnings and describe IDC amortization/AMT consequences. [2025 Form 4797 instructions](https://www.irs.gov/instructions/i4797) describe section1254 recapture involving deducted IDC/depletion. [New Jersey partnership guidance](https://www.nj.gov/treasury/taxation/njit11.shtml) distinguishes partnership-category income from cash distributions. These authorities motivate separate supplied channels; they do not validate this illustrative partnership or future-year eligibility.

## Actual money and independent tax facts

One existing household wallet funds actual calls. Supplied recourse can consume cash beyond contributed investment capital. Production units times entered commodity prices, less entered royalties, supply actual cash; paid operating costs, fees, claims, IDC and tangible acquisitions consume it. Unpaid creditors persist. Creditor liability reduces household wealth once; an unmet capital-call constraint is reported separately rather than charging the same creditor twice. Unfilled distributions never become household receipts. Product failures and mandatory household spending/tax failures remain separate diagnostics. In a blended option household, the explicit option priority runs before product sleeves; actual released premiums can fund a later drilling call. Both validators reject shared owned accounts or known reference wash groups that require a coordinated lot-book adapter. Uncovered sleeve, option and drilling liabilities reduce wealth once; creditors already netted in NAV are not subtracted again.

Federal/NJ outside basis, tangible-cost pools and federal at-risk balance remain separate. Actual paid IDC and tangible acquisition pools bound applicable supplied deductions; no production permits no modeled depletion. Depletion is an independently supplied, prelimited amount, not a guessed statutory percentage. Basis/at-risk reductions are also separately supplied and bounded by actual available amounts. Independent basis/at-risk/passive/other caps limit federal and NJ deduction facts. Allowed, denied and dated deferred recognition remain separate. Requested amounts above supplied caps remain unrecognized in the audit; this slice does not infer carry eligibility. Deferred events survive an earlier economic exit.

Supplemental prelimited SE, eligible QBI and current AMT additions use the existing validated tax adapter. Ordinary NIIT exclusion requires its own supplied non-section1411 classification, independent of the GP/working-interest label and box14 earnings. [2025 Form8960 instructions](https://www.irs.gov/instructions/i8960), lines4b and the self-employed special rule, support this distinction; the older 2023 instructions discovered/read locally were verified against these current official passages. Zero SE needs an explicit independent classification rationale. Unsupported generated SE plus SSA/IRA earned-income combinations block rather than omit earnings. Current AMT is included; AMT-credit history, statutory depletion/IDC eligibility, QBI loss history, debt allocation/relief, distributions above basis/at-risk and cross-border returns require other adapters. `full_tax_optimization_supported` is always false; every reported after-tax outcome is conditional on supplied facts and these limits.

## Exit and matched liquid alternative

A property sale creates cash once, pays modeled creditors, recognizes funded costs and applies independently supplied ordinary-recapture capacity plus supplied residual capital holding character. Federal/NJ bases, exit-loss caps/timing and NJ category remain independent; a loss in one jurisdiction cannot erase a gain in the other. An unpaid creditor/call blocks completed liquidation and remains visible. The full-cash liquidation request is atomic: if proposed sale proceeds plus cash cannot pay every modeled creditor and exit fee, or a capital call remains unmet, no property sale or sale receipt executes. The unsold property, its supplied production and all creditors carry into later months. Partial property sales require a separate inside-basis and dated tax-recognition adapter; no favorable partial-sale tax timing is inferred. Post-exit new cash/basis operations require a settlement adapter; final supplied tax facts can still arrive.

The alternative starts with identical household wealth and requests the same capital budget. Actual share purchases, FIFO sales, separate federal/NJ basis and wash recognition reuse the ordinary lot book. Separate reference cash requests and sale locks are editable; no well-specific cost or K-1 allocation is copied onto ETF shares. Price-only returns and zero fees are explicit assumptions. Opening reference shares begin their holding clock at scenario start, a conservative declared new-investment comparison; historical holding credit is unsupported. Complete forward wash context requires explicit no-external-identical-trade confirmation; carried unfunded calls that could buy within30days also keep the window pending; an unresolved December window with a modeled future buy blocks annual reconciliation. Gains/losses stay in the sale year.

Existing annual returns, actual dated withholding/payments/refunds and accrued unpaid tax feed both household projections. Comparison reports cash, liabilities, product value, actual annual tax and conditional net wealth. No deduction-times-rate amount is deposited. The two-year synthetic base loses $41,600 before tax versus flat liquid shares; its actual configured tax difference is only $721.07. Poor production and denied/deferred examples expose unfavorable outcomes rather than turning headline deductions into profit.

## Reproducible checks

Independent checks reconcile contribution/cost/distribution/exit conservation; actual recourse exceeding original capital; creditor and call nonduplication; separate federal/NJ basis, noncash depletion/depreciation and limitations; positive recapture with denied/deferred losses; delayed recognition after exit; actual share gains, locked exits and December recognition; annual liability and unpaid-tax reconciliation; unknown-source rejection; and actual editable UI submission with stale-result clearing.

The shared life-policy ledger executes before drilling, retaining its actual
premium funding, failure exits and independent insurance-income/NIIT adapter.
Mixed synthetic checks show a $1,000 premium leaving $500 of the drilling call
and its underlying creditors unpaid without duplicating that debt, and an actual
$500 MEC policy loan completing the drilling call while preserving the policy
loan, recognized income and additional tax exactly once. Policy net surrender
equity and drilling net property equity both survive the generic Household audit.

Each deduction now requires a separate `basis_effect_source`. Its audit retains
requested and actually applied federal/NJ outside-basis, at-risk and tangible
pool reductions with before/after balances. Denied current recognition does not
itself determine those independent effects. The actual 2025 K-1 instructions,
page 25 box 18 code C, discovered/read through QMD and verified against the
[official instructions](https://www.irs.gov/instructions/i1065sk1), distinguish
nondeductible expenses from their outside-basis reductions. [Publication 541
(December 2025), Adjusted Basis](https://www.irs.gov/publications/p541) likewise
identifies nondeductible noncapital expenses. These authorities do not qualify a
particular denied IDC/depreciation item or infer its at-risk/NJ effect. A source
must supply each effect; omitted provenance blocks the input, and actual funded
pools still cap every applied reduction. Regressions show denied tax recognition
with separately supplied zero/nonzero basis effects and an over-request capped
to the actually paid cost, without a tax deduction or fictitious cash.

Optional liquid-saving purchases execute after required drilling funding. In a
shared synthetic wallet with $100,000, the full drilling call executes before an
unfilled $500 January saving request. Later actual distributions fund $1,000 of
new share lots. The flat-share case preserves $41,600 before actual tax, with
both account books and their generic Household audits retained.

The final audit exposes raw executed `terminal_state`: actual `closed` and
`property_sold` flags, cash, residual property, each creditor, unpaid calls,
outside/at-risk and tangible bases, plus actual reference cash, exit-pending and
pending wash losses. Existing reference lots/disposals and future tax events
remain beside it. A zero property mark or net account balance does not establish
a sale or a completed tax exit; consumers must verify every applicable state.
This audit does not change liquidation, tax timing or funding priority.
