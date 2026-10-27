# Complete zero-opening new-life offers

An optimizer may select among independently supplied complete new-issue paths
without inventing policy values or moving opening cash into a free insurance
asset. This helper depends on the native uninsured/new-issue seam in
[ADR0105](0105-uninsured-and-zero-opening-new-issue.md). Shared optimizer input,
compiler and UI wiring belong to the integrating owner; this unpublished layer
adds only the offer record, validation/application helpers and runnable checks.

`wealthlab.optimization.new_life_offers` exposes `NewLifeOffer`,
`validate_offers(household, offers)` and `apply(data, offers, selected_ids)`.
`NewLifeOffer` is defined in `new_life_inputs` and re-exported by that API module.
It is an immutable source record containing an explicit owner, complete native
`LifeHolding`, source description and matched-new-issue confirmation. A holding
contains only an account ID; a birth date cannot identify an owner when household
members share one. No new independent insurance need is inferred from the quote.

## Zero opening capital and complete supplied schedules

Every offered owner must already have an independently supplied need in the
baseline `life_plan`, which may have an explicit empty holdings list. No offered
destination may replace any existing account or policy, even an account with zero
balance. All opening cash, surrender and death values, known federal investment
and loan debt must be exactly zero. The source quote must be available by the
household opening date, and opening/issue/start dates must match that date.

The first policy event must be an actual positive premium; all earlier supplied
values and coverage must remain zero. A complete full terminal event must be
supplied inside the exclusive household horizon. This is a bounded offer profile,
not an automatic future surrender instruction. No initial fee-only, free-coverage,
pre-existing zero-equity or unexecuted terminal-value profile is inferred.
Changing the illustration requires another complete supplied path, not scaling
premiums, cash values, benefit, eligibility, costs or exit proceeds.

Each offer is inserted into an independent trial copy and validated by the
existing native household policy adapter. It retains its qualification, MEC,
independent NJ recognition, owner birth date, monthly post-event values, reserve
calendar and required-payment failure settlements. Unknown or incomplete terms
block even an inactive offer. The helper establishes no underwriting entitlement,
insurer quote accuracy, statutory eligibility or full-tax optimization certificate.
The underlying contract/tax boundaries remain [ADR0102](0102-whole-life-contract-cash-and-tax.md)
and [ADR0103](0103-household-whole-life-funding.md); this layer adds no tax law.

## Atomic whole-offer selection

Offer IDs must be unique. Alternative illustrations may share a destination
account, but selecting both is rejected. Duplicate or unknown selections are
rejected. `apply` validates **every** offer and all selected destinations before
mutating the compiler's raw JSON dictionary; an invalid inactive quote cannot
hide behind the no-policy choice. Selecting none leaves the original dictionary
unchanged, including all cash and independent insurance needs.

Selected offers append only zero-balance USD insurance accounts and their complete
native holdings. Existing accounts/holdings, needs, wages, tax facts, spending and
other product plans remain intact. No premium cash, loan, investment basis or
protection is injected during selection. The existing chronological native policy
book later pays actual premiums from the same household wallet (or its explicitly
permitted funding sales), executes supplied failure settlements, cancels later
coverage/events after failure, and recognizes actual terminal cash/tax once.

## Independent checks

A $10,000 household retains its full $150,000 uninsured need and $7,000 closing
cash when no offer is selected. Selecting the complete supplied policy starts
with exactly the same $10,000 capital, pays $2,000 dated premiums and receives
$2,100 actual surrender cash, leaving $7,100 after $3,000 spending and recognizing
$100 federal/supplied NJ income. Only $500 available causes the first premium to
fail; the household retains $500, no coverage or premium basis, and no later
illustrated receipt. These remain synthetic conditional values, not insurer terms.

Other checks cover all five zero-opening components and unknown investment,
source availability, owner identity with matching birth dates, fixed existing
needs/holdings, no existing-account replacement, complete premium/failure/value/
tax/exit schedules, mutually exclusive destinations, duplicate/unknown identities
and unchanged inputs after invalid active/inactive selections. Native insurance
and existing life-path regressions remain required. Broader combined wallet,
optimizer menu, training/validation and UI evidence belong to the integrating
owner, not this helper-only layer.
