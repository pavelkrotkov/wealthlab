# ADR 0020: Current-year deposits share the ordinary IRA cash and basis ledger

Status: combined annual IRA contribution/withdrawal layer of open retirement ticket #6. The household withdrawal bridge still excludes these deposits until its dynamic funding adapter is implemented. This workbench does not establish household spending safety or pay income taxes.

The existing contribution case is an optional nested input to the ordinary IRA case. Its year, opening cash, owners, births and account book must match; this is one opening cash amount, not two sources. Only ordinary traditional/Roth IRA contributions belong here. All current-year deposits and external cash receipts must be listed, with confirmed compensation, MAGI, workplace coverage and complete elections. Prior-year deposits after year end, excess corrections, recharacterization, workplace and inherited products remain unsupported.

One dated timeline applies receipts, returns, withdrawals/conversions, then contributions on the same day. Supplied order breaks ties. Contribution capacity and deductibility reuse the existing tested functions. Only actual funded deposits consume room, enter accounts or add basis. Earlier failed requests are not retried after a later receipt. A later deposit cannot fund an earlier withdrawal, while annual tax aggregation can still use current-year contributions as required. Opening December values remain the RMD base.

The maximum computed federal deduction leaves any nondeductible traditional contribution in federal basis. New Jersey traditional basis adds the full funded contribution. Funded regular Roth deposits add to federal regular-contribution and separate NJ basis; the first actual Roth contribution can establish its tax year. Annual withdrawal ordering consumes regular Roth basis before conversion buckets. These operations reuse the existing traditional/NJ/Roth reconciliation, rather than treating deposits as investment returns.

## Completed tax checks and conditional scope

The federal tax adapter maps the allowed IRA deduction to Tax-Calculator's existing `e03150` input. NJ receives no IRA deduction. A supplied annual tax case must exclude the modeled IRA income and deduction. The tax-only comparison holds funded contributions and their deduction fixed on both sides; it is not a fully re-optimized alternative contribution policy. No modeled tax liability is paid from this workbench cash.

When an annual case is present, supported W-2 compensation must cover funded deposits. Completed MAGI must support the maximum deduction actually computed and every funded Roth deposit. For the implemented inputs, traditional-IRA MAGI refigures AGI without the IRA deduction; Roth MAGI additionally removes taxable conversion income. A stale forecast that changes the maximum deduction or permits an ineligible Roth deposit blocks the result. Negative MAGI is distinct from negative compensation and is accepted as a forecast.

Social Security deduction worksheets and AGI-dependent passive losses require later adapters and block this combined annual tax profile. Other compensation sources require a supported adapter instead of being inferred from investment income. Without an annual tax case, the result explicitly states that eligibility rests only on supplied annual forecasts. It does not claim to have checked actual compensation or MAGI. The household/optimizer must use completed scenario income when those adapters land.

## Reproducible synthetic case

The example begins with $10,000 cash, $100,000 traditional IRA and $50,000 Roth. It funds $3,000 traditional and $3,000 Roth deposits, then withdraws $10,000 traditional, converts $20,000 and withdraws $25,000 Roth. Cash ends at $39,000; traditional assets are $73,000 and Roth $48,000. Cash plus assets remains $160,000 before taxes, exactly opening capital; deposits and conversion create no wealth.

The $3,000 federal deduction adds no federal traditional basis; NJ basis adds $3,000. Annual traditional basis remaining is $14,174.76 federally and $37,563.11 for NJ. Roth's new regular deposit reduces conversion recapture to $1,200. Frozen-2025 federal tax inputs produce $121,174.76 AGI; the eligibility audit shows $124,174.76 traditional MAGI and $108,058.25 Roth MAGI after removing the taxable conversion. Cash is labelled remaining cash, rather than gross cash received.

Tests cover these reconciliations, short deposits, late annual Roth ordering, zero earlier principal, first Roth year, unchanged exports, duplicate opening context, unsupported tax inputs and the real workbench. A modeled capital gain that removes Roth eligibility is rejected; a changed maximum IRA deduction requires an updated forecast.

## Dated primary references

Checked October 24, 2026. QMD discovery found the 2025 Form 1040 instructions' warning about special Social Security deduction worksheets; it did not supply the full combined calculation. [IRS Publication 590-A (2025)](https://www.irs.gov/publications/p590a), Worksheets 1-1, 2-1 and Appendix B, supplies the MAGI distinctions and special-benefit worksheet boundary. Its deduction and contribution rules remain those reused by [ADR 0005](0005-retirement.md), with separately labelled 2026/frozen assumptions.

[IRS Publication 590-B (2025)](https://www.irs.gov/publications/p590b), Roth aggregation rules and RMD account-balance discussion, distinguishes annual contribution ordering from dated assets and prior December values. [NJ's 2025 instructions](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf) and [NJ deduction guidance](https://www.nj.gov/treasury/taxation/njit13.shtml) support separate state contribution/basis treatment. These sources do not establish personal compensation, actual IRA history or later-year law.
