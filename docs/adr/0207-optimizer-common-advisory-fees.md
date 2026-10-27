# ADR 0207: Common sourced advisory fees in native policy search

Status: unpublished consumer above [ADR0078](0078-household-outer-advisory-fees.md) and [ADR0079](0079-advisory-observed-snapshots-and-advance.md), combined with native option/new-life allocation ancestry for [issue #18](https://github.com/pavelkrotkov/wealthlab/issues/18). No public parent is rewritten by this integration.

## One contract, fresh actual execution

The optimizer accepts `household.advisory_fee_plan` as a common source assumption. Choices cannot edit or clear it, and candidate compilation verifies the complete contract remains identical. All source, period, valuation, marginal-tier, embedded-versus-outer and cash-pool guards remain native. Every candidate, held-out sample and robustness run constructs its own fee ledger from actual native balances and source-approved observed snapshots. No supplied AUM, scaled historical snapshot, new capital, additional wallet or tax deduction is introduced.

Every offered strategy account must have explicit common fee coverage, including locked/inactive offers. New accounts require source-confirmed `if_present` coverage, with a supported native net-equity or life net-cash/net-surrender basis. Genuine common source-confirmed exemptions can use a zero-rate schedule; omission is not a cost-free choice. Declining an investment does not imply account absence: a native present zero account remains an observed zero balance. This rule covers option, sleeve, exchange, life and the declared drilling/QOZ offer interfaces. QOZ alternatives retain the original zero-opening account; coverage does not create new capital or a new QOZ account. Existing baseline account coverage remains the supplied contractual scope.

Adding or changing a fee contract changes a complete source-envelope fingerprint. The consumer does not reseal or reconfirm drilling/QOZ tax-validity envelopes automatically, even for a synthetic input flag. Those combinations need their own independently supplied matching envelope; a fingerprint certifies no legal or financial fact.

## Actual cash, evidence and ranking

The combined product order retains required native books and canonical QOZ source-year returned results, then advisory assessment, with `SavingLedger` last. Later optional wrapper reservations and gross-cash required funding remain the original fee adapters. Broker commissions, embedded costs and outer advisory fees stay separate; original shares/basis and new-policy premium funding are unchanged.

Assessment reports median actual advisory assessments, median actual paid cash and maximum ending advisory fee debt. Missing actual fee observations are not reported as zero cost. An outstanding aggregate modeled fee liability or missing/mismatched native advisory execution audit prevents completed-exit ranking; all existing share, gross-position, loan, contract and tax obligations remain checked. This establishes modeled fee-balance clearance, not universal legal termination of an adviser engagement or future unspecified services.

An original flat example begins with $300,000, pays $48,000 spending and a $1 original-stock commission, and allows zero/one/two cash-funded option units and a separately supplied new policy. Each option unit earns $496; the policy pays $2,100 after $2,000 actual premiums. A common 2027-only 1% terminal-year invoice uses actual pre-December-spending assets. Zero units/no policy pays $2,539.99 and leaves $249,459.01. Two units plus the policy pays $2,550.91 and leaves $250,540.09, without adding initial wealth or changing source terms. Held-out execution keeps the same contract. A $350,000 stress invoice pays only $253,999, retains $96,001 actual fee debt and receives no completed-exit value.

## UI and supported boundary

Optimize offers an original common sourced-fee starter after native strategy menus. Imported real contracts remain editable JSON; the starter refuses to replace an existing contract or create a quote for a nonsynthetic household. Candidate/validation tables expose paid fees and debt beside actual after-tax exit wealth. Fee assumptions are not an optimization dimension.

Native supported monthly cutoffs, source-confirmed advance/refund assumptions and unavailable/first-day timing guards remain unchanged. Entered billing periods and coverage are the source model; no ongoing contract beyond those supplied terms is inferred. Actual adviser-specific completeness, legal eligibility and unsupported valuation bases remain outside this bounded consumer. Public examples contain only original synthetic terms.
