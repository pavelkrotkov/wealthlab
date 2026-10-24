# ADR 0006: IRA withdrawals and conversions

Status: second layer of retirement ticket #6. Contribution PR #28 precedes this layer; the full retirement ticket remains open.

This annual workbench supports explicitly identified ordinary traditional/Roth IRAs. It requires confirmation that all owner's IRA accounts, prior basis and conversion history are included, with no prior deferred RMD, outstanding rollover or current-year regular contribution. Those histories need the later household integration. Workplace and inherited accounts cannot be substituted merely because their wrapper is traditional/Roth.

Fixed schedules execute in date order, with returns before same-day orders and stable order priority. Withdrawals reduce the actual source balance and add cash once; conversions transfer funded assets without creating cash. Unfilled requests stay visible. Later returns cannot fund earlier requests. The input and output JSON remain local and exportable.

## Annual recognition

Federal traditional basis aggregates every configured traditional IRA of the owner, including accounts without withdrawals. Annual pro-rata recovery uses ending value plus funded distributions/conversions. Separate NJ basis uses its own combined-owner traditional pool. Cumulative cent allocation preserves total recovery and basis even with partial events or losses. This is a planning calculation, with full decimal precision before cent rounding, rather than a prepared tax form.

Federal Roth ordering uses regular contributions, annual chronological conversion buckets (taxable portion first), then earnings. The qualified-distribution clock and conversion-recapture clocks remain separate. Qualification here requires both five tax years and the actual age-59½ date. Qualified distributions consume the recorded principal pools without becoming taxable. Annual grouping can change recognition of an earlier withdrawal after a later conversion, but never supplies that earlier event with future cash. Reconciled results are not available to earlier policies.

NJ nonqualified Roth earnings use a separate proportional worksheet calculation, independent of federal ordering. Full converted principal enters NJ Roth basis because it combines previously taxed basis with amounts recognized on conversion. Traditional and Roth NJ pools stay separate. Mixed qualified/nonqualified Roth withdrawals within one year are explicitly rejected pending a validated NJ allocation model. Disability, death and first-home Roth qualification are unfinished; a supplied early-penalty exception is conditional and does not by itself make a distribution qualified.

Taxable early withdrawals and recent taxable conversion principal have a separately calculated ten-percent additional tax, subject to the age/explicit-exception assumptions. The existing Tax-Calculator input `e09900` includes it once in annual liability without increasing AGI or payroll income. An optional annual forecast supplies other income and fixed deductions, excluding these modeled flows. Federal/NJ tax ages are validated separately, including January-first birthdays. Age-62 NJ pension exclusion qualification is owner-specific; younger-owner disability eligibility is unfinished. Tax liability is reported without being paid from the workbench's cash.

## Required withdrawal targets

The engine reuses the pinned Owl IRS Table II/III data, passing an explicit scenario year. It does not call Owl's host-date-dependent RMD projection helper. The selected beneficiary table applies to all the owner's configured ordinary IRAs; differing beneficiary arrangements need separate future modeling. Current-year cash withdrawals satisfy the target; conversions do not. Conversions block while the owner's target is unmet. No withdrawal or borrowing is invented to repair a target shortfall.

The schedule targets December 31, including the first RMD year. First-year April deferral, prior arrears and shortfall excise tax remain excluded; an unmet target is not a complete tax-penalty determination. The law/table regime is held constant for forward assumptions. For the 1959 birth cohort, the current regulation still reserves the applicable-age paragraph: the user must choose an explicit conditional age-73/75 scenario when RMDs become relevant.

## Primary checks and reuse

Checked October 23–24, 2026. [2025 Form 8606](https://www.irs.gov/pub/irs-pdf/f8606.pdf) supplies owner-wide basis and year-end valuation structure; [IRS Publication 590-B (2025)](https://www.irs.gov/publications/p590b) supplies holding clocks, early-tax distinctions and RMD tables. [26 CFR 1.408A-6, A-8/A-9](https://www.ecfr.gov/current/title-26/section-1.408A-6) establishes annual Roth ordering/grouping. [2025 NJ-1040 instructions, printed pages 14–15](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf) and [TB-44(R), February 2010](https://www.nj.gov/treasury/taxation/pdf/pubs/tb/tb44.pdf), still referenced by those instructions, establish the separate NJ treatment. [26 CFR 1.401(a)(9)-2(b)(2)](https://www.ecfr.gov/current/title-26/section-1.401(a)(9)-2) identifies published RMD cohorts and the reserved 1959 paragraph. Installed Owl 2026.10.10 provides the table data; eligibility and account ownership remain our ledger's responsibility.

Spending/tax cash integration, current-year contribution reconciliation, workplace withdrawal rules, HSA/education, full exception eligibility, benefit/healthcare timing and matched Owl retirement comparisons remain required under #6.

[ADR 0020](0020-current-year-ira-deposits.md) now adds confirmed current-year regular deposits to this annual cash/basis workbench. Its documented tax checks and unsupported special worksheets qualify the earlier contribution exclusion; household deposit funding remains unfinished.
