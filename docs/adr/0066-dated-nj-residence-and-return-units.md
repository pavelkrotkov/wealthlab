# ADR 0066: Dated NJ residence and independent state-source return units

Status: accepted, conditional supported profile. Date: 2026-10-25.

## Decision

`AnnualCase.nj_residence` optionally supplies stable people/filing roles, complete legal NJ residence periods with exclusive ends, independently measured NJ income/source rows, actual period deductions and per-return payments. Address or travel does not establish domicile. Full-year US citizenship and legal residence facts are explicit confirmed assumptions. Federal worldwide income, payroll and foreign-tax credit calculations remain independent.

The adapter reuses the existing NJ rate table, deduction and exemption calculations. NJ-1040 includes worldwide resident-period income. NJ-1040NR calculates tax on worldwide nonresident-period income, then applies NJ-source column B divided by column A, rounded to four decimals. That percentage can exceed one. Full-year gross controls the filing threshold. Resident and nonresident fifteen-day month counts independently prorate basic/age/dependent exemptions; actual medical/MSA/health, alimony and conservation expenses use their supplied period. Signed disposition losses net within the relevant period/category. Classified nonresident line-22 pension income has no NJ-source column entry.

Joint federal filers with common state periods can follow joint filing. The explicitly confirmed mixed-residence spouse exception and full-nonresident sole-source-spouse exception create separate NJ return units without changing the federal joint unit. The older spouse's state exemption stays with that spouse. Different spouse dates do not silently elect worldwide joint resident taxation. Mixed-period joint elections and separate-return dependent allocation remain unsupported.

## Actual consumer

Cross-border / **NJ residence / move** edits either an annual case or an actual household with the existing foreign-tax book. The household observes source rows only through each month end, reconciles recognized NJ amounts exactly, and uses the existing `TaxLedger`, wallet, required funding and `payments.pay`. The actual positive year-end NJ payment is allocated to stable resident/nonresident return IDs. An unpaid return remains debt; no predicted refund funds another bill. No NJ tax cash or foreign withholding is paid twice.

The current move cash profile requires no opening/scheduled/payer NJ prepayments and year-end settlement. Standalone supplied annual payments must reconcile to actual return identities. Overpayments, refund/other-return payable combinations and liability revisions requiring reallocation reject explicitly; the subsequent shared jurisdiction cash-book extension must preserve their independent claims. Unsupported realized source/basis facts fail reconciliation rather than inheriting federal lot basis or obtaining a favorable zero.

## Primary authority and discovery

QMD `tax-references` vector discovery identified the **2025 NJ-1040 instructions**; older 2023/2024 hits were inspected and excluded from numeric authority. Official public documents were independently read and relevant tables/pages visually checked on 2026-10-25:

- [2025 NJ-1040 instructions](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf), printed page 5: resident-period reporting, full-year filing threshold, fifteen-day proration and a separate nonresident return where applicable.
- [2025 NJ-1040NR instructions](https://nj.gov/treasury/taxation/pdf/current/1040nri.pdf), printed pages 4 and 25: specific spouse filing exceptions, part-year reporting, four-decimal percentage and the official $50,000 NJ gain/$10,000 other-state loss example producing 125%. Printed pages 38–39 independently establish the $39,000 and $49,500 single/separate table cells used in checks.
- [GIT-6, May 2026](https://www.nj.gov/treasury/taxation/pdf/pubs/tgi-ee/git6.pdf), resident and nonresident exemption/expense sections, including printed page 26: independent nonresident month proration and actual period expenses. Its older numerical examples do not replace the 2025 tables.
- [NJ credit for other jurisdictions, updated September 28, 2026](https://www.nj.gov/treasury/taxation/njit14.shtml): no credit is inferred for PR or foreign-country income taxes.

## Checks and limits

Independent checks cover two actual returns totaling $1,741.60, the official 125% source-ratio example, four-decimal rounding, full-year thresholds, thirteen combined resident/nonresident counted months, post-move pension sourcing, actual period medical costs, spouse identity/age exceptions, denied/unknown facts, actual allocated settlement and insufficient cash. The combined foreign/NJ household keeps US employee payroll $7,650 and actual US FTC $6,724.50 separate; $50,000 opening cash less $11,000 foreign tax and US/NJ settlement leaves $30,533.90.

Published numeric rules are 2025 only; later years require explicit frozen-2025 policy. State retirement exclusions, business/carry categories, special deductions/exemptions/property credits, other-jurisdiction credits, independently allocated NJ prepayments/refunds, noncitizen federal residence, PR/Spain assessment execution and treaty/FTC redetermination remain separate supported-profile work. This layer supplies state residence execution; it does not complete issue 17.
