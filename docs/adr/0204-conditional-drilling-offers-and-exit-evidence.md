# Conditional drilling profiles, source scope and actual exit evidence

This unpublished optimizer helper consumes the native household and price-path
adapters in [ADR0091](0091-conditional-drilling-partnership.md) and
[ADR0092](0092-drilling-realized-price-bindings.md). It adds no wallet, return,
valuation or tax-law engine. Shared optimizer schema/compiler/UI/scope and market
binding selection belong to the integrating owner.

## Source envelope

`drilling_inputs.DrillingEnvelope` is an independent source record with an as-of
date, validity-through date, source description and explicit confirmations for
**all** candidate employment, income and funding states and bound commodity/
reference paths. Legal classification, supplied SE/QBI/current-AMT/history,
limitation, recapture and release facts must remain valid throughout that scope.
The source must be known by household opening, cover the modeled horizon and
extend through every supplied release date, including post-exit recognition.
`full_tax_optimization_supported` is literally false and cannot be enabled.

The integrating owner passes the complete normalized `PolicySearch` JSON dump,
excluding `drilling_envelope` itself. `drilling_scope.fingerprint` uses standard
canonical JSON plus SHA256; it does not flatten unknown objects or nonfinite
values to strings. A changed search input, offer, binding or menu needs a newly
matched envelope. The original household must remain in that scope. This is
change detection **only**, not source authentication, legal certification or a
calculation of statutory limits. A matching hash cannot override unsupported
native combinations, unconfirmed facts or a changed legal/rate term.

## Complete supplied offers

`drilling_inputs.DrillingOffer` supplies a complete native `DrillingPlan`, source,
source date and matched-terms confirmation. All inactive offers are validated too.
Only complete source-supplied absolute economic/tax paths may vary; the helper
never infers proportional production, fees, basis, deductions, SE/QBI/AMT facts,
recapture or exits from a capital amount. Relationships between these dollar
profiles remain opaque independently supplied assumptions.

The original account ID and every opening cash/property, federal/NJ outside basis,
federal at-risk and tangible pool stay fixed. Legal, recourse, classification and
other fixed contract assumptions remain unchanged. Observation dates, commodity
and reference unit prices, royalty fractions, entered dealing locks and exit
request dates stay fixed. Different profiles may explicitly supply different
absolute calls, quantities, costs, distribution/property/exit amounts and prelimited
tax caps/timing. Existing native funded-cost/basis/risk guards still apply at
execution. An actual-versus-liquid-reference mode change requires every prior opening
component to be zero and explicit independently supplied confirmation of no prior
interest or obligations. An existing well cannot become reference stock through
a counterfactual initializer: it needs an actual modeled taxable transfer first.
Same-mode profiles preserve existing capital. Reference stock tax recognition
never inherits well deductions.

`drilling_profiles.validate_offers` validates the original account, envelope,
identities and every complete offer in its own freshly validated native trial.
`drilling_apply.apply(data, offers, selected_id, envelope, search_scope)` checks
all inactive terms and selection before changing only `drilling_plan`. The caller
supplies a valid candidate produced from the declared search scope; candidate
employment/income/funding can differ within that independently confirmed scope.
No cash/account balance, original capital, tax model or other product plan is
changed by selection.

A no-entry offer may instead have `plan=None` only with explicit confirmation of
no prior interest or obligations and no new entry. Every prior opening cash,
property, outside/tangible basis and at-risk component must be zero. The original
zero account remains; a zero marked value alone never grants this legal assumption.
The integrating owner clears the unused drilling market binding, and owns its
explicit cash-only market scope when no active investment binding remains.

## Closure proof

`drilling_exits.completed(household, row)` consumes actual final native audit
state. An actual property interest requires both executed `closed` and
`property_sold` flags, zero owned-account value, cash/property, every modeled
creditor, unpaid calls and all outside/at-risk/tangible pools. Deferred/unrecognized
future tax events prevent completion even after physical sale. A worthless unsold
property or clipped zero equity cannot count as liquidation.

Liquid-reference mode instead requires actual empty reference lots, zero reference
cash, no pending exit or federal/NJ wash losses and no unpaid capital request or
future tax facts. Unused shadow property-book flags/bases are not real reference
positions. Missing required fields, malformed or nonfinite amounts and unknown
book state fail closed. This proves modeled book closure, not release from every
possible legal liability, full household tax settlement or unsupported AMT-credit/
other historical tax rules. Those limits and unresolved risks remain disclosed.

## Independent evidence

Full well, liquid-share and explicit no-entry profiles preserve original $200,000
household capital and execute only their actual cash flows. A separately supplied
$40,000 profile retains a $10,000 flat manager fee and $25,000 property exit quote;
it is intentionally not a proportionally scaled $100,000 illustration. Native
execution leaves $185,000 cash. No-entry leaves $200,000 and creates no deduction
or tax-saving receipt. A sold property with a later deduction release still fails
completed-exit proof.

Runnable checks exercise source/date/fingerprint changes, unknown confirmations,
inactive invalid offers, fixed opening/legal/unit terms, every no-entry prior
component, atomic selections, actual cash conservation, native actual/reference
closure, pending tax/wash/cash/calls/creditors and missing/malformed evidence.
Broader optimizer menus, joint feasibility, UI and paired selection/validation
samples remain the integrating owner's work; this helper-only layer makes no
standalone optimizer-readiness claim.
