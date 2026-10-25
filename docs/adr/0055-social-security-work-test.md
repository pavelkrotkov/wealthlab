# 0055: Own-record employment work tests separate forecasts, assessment and cash

Status: accepted as a bounded workbench layer of open retirement issue #6.
Extends [ordinary claims](0010-social-security.md). Household/tax integration
and auxiliary/survivor work effects remain separate work.

Retirement / **Social Security with employment** accepts editable/imported JSON
with one own-record work report per member and calendar year. Its nested claims
object is explicitly the no-work counterfactual; the work policy supplies separate
reported wage forecasts and actual current US W-2 earned wages. Earlier cash uses
forecasts, never realized future wages. Annual wage limits are frozen at the
2026 lower$24,480 and FRA-year$65,160 levels, with monthly$2,040/$5,430 limits;
these are assumptions for later years, not forecasts of future law. The FRA-year
annual test counts only earnings before the FRA month. Deduction amounts floor
to whole dollars after the one-half/one-third calculation.

The first entitled pre-FRA non-service month establishes the initial grace year;
it is not an elective policy. Prior grace-year usage is explicit. The monthly
test protects non-service months in that year, even with larger pre-claim wages.
Forecasts can use already-observed prior-year grace history. The next year's
forecast does not use that next year's realized wages. A zero-dollar benefit
while otherwise entitled does not postpone the grace year.

Initial cash withholds whole checks. Closed-year actual wages determine the
legal full/partial charges. A last partial charge creates a later refund, and
unexpected excess benefits create overpayment debt; annual excess beyond payable
benefits creates no additional debt. Receivables and debt are carried separately
by recipient. A prior-year liability cannot include a December entitlement that
has not yet been paid in January. Due refunds first offset the same recipient's
due debt, then become cash; the supplied recovery fraction applies only to
current available benefits. Future-due claims cannot fund current recovery.
The entered settlement month and recovery fraction are explicitly conditional
administrative assumptions, not modeled SSA notices, waiver decisions or legally
validated collection schedules.

Actual full or partial work deductions credit the own-record early-reduction
factor. The adjusted entitlement starts at FRA using the existing source-backed
dime/dollar arithmetic and projected PIA. Its processing month in the following
year is supplied conditionally. Earlier increases become arrears when the FRA
year closes and are paid only at processing; current increases start then.
Government positions do not enter spendable cash on recognition. The baseline
OWL comparison remains a no-work counterfactual; it is not presented as a check
of these work-test calculations.

The synthetic independent POMS example has$562 monthly benefits and$2,881 excess:
six whole checks withhold$3,372, the final partial charge is$71, and$491 is paid
in the supplied following-May settlement. Six credited months change a$803 PIA's
60-month early reduction to54 months: the issued benefit rises from$562 to$582.
With May2032 processing after a January2031 FRA,15 earlier payments add$300
arrears; May2032 cash is$882. Checks cover these amounts, FRA cutoffs, monthly
grace history, future-wage prefix invariance, recipient isolation, overpayment
collection, cash-plus-government-position conservation, invalid scope and UI
editing/submission. No aggregate tax-savings receipt is created.

The initial profile requires complete current earned-W2 classification without
special payments, no opening work-related government positions or reduction
credits, no claims preceding the projection start, no other auxiliaries, and no special lump-sum tax election. It rejects
actual spouse/survivor add-ons and dated deaths. Self-employment, foreign work,
family allocation, opening debt/waivers, earnings-history PIA reconstruction,
Medicare collection and household tax recognition need their own supported
adapters. The fixed PIA is a supplied assumption despite continued employment.
This screen is neither an eligibility determination nor a retirement-safety result.

Primary sources inspected October25,2026:

- [POMS RS02501.025, annual/monthly exempt amounts](https://secure.ssa.gov/poms.nsf/links/0302501025), 2026 table.
- [POMS RS02501.080, excess earnings and FRA-year cutoff](https://secure.ssa.gov/poms.nsf/links/0302501080).
- [POMS RS02501.030, initial grace year and non-service months](https://secure.ssa.gov/poms.nsf/lnx/0302501030).
- [POMS RS02501.100, full-month withholding](https://secure.ssa.gov/poms.nsf/lnx/0302501100).
- [POMS RS02501.110, closed-year partial payments](https://secure.ssa.gov/poms.nsf/lnx/0302501110), example1.
- [POMS RS00615.480, adjustment effective dates](https://secure.ssa.gov/poms.nsf/lnx/0300615480).
- [POMS RS00615.482, reduction-factor crediting months](https://secure.ssa.gov/poms.nsf/lnx/0300615482).

Claims must begin on or after January 1 of the start year. The ordinary no-work
baseline can include a prior December entitlement paid in the first January,
but this work profile has no prior-year assessment, opening adjustment or ARF
credit history. Rejecting an earlier claim prevents that payment from silently
escaping withholding. Extend the projection backward to cover the claim before
using this profile; an existing claimant needs a separate opening-history adapter.
