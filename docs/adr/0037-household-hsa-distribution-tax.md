# ADR 0037: Household cash-HSA distribution taxes

Status: another retirement slice under open #6. Reuses the existing cash-HSA/receipt engine, ordinary-income adapter and actual household tax ledger. Current medical bills, HSA investments/state basis, corrections and beneficiary transfers remain separate work. No new dependency.

## Funded amounts and explicit classification

A household HSA order may now request `allow_nonqualified`. The existing HSA book first determines the cash actually available and consumes eligible, already-paid historical receipts. The funded amount minus the qualified portion is the federal taxable amount. The existing dated age65/disability exception logic removes the additional20% tax when applicable; it does not exempt ordinary income. Unfunded requests create neither income nor additional tax. Receipt balances stay global across years/accounts; no new unpaid bill becomes an eligible receipt.

The first supported nonqualified household profile requires an explicit `ordinary_noninvestment_assumption`, confirmation that generated distribution taxes are absent from other inputs, and an independent supplied NJ taxable fraction for every nonqualified order. The federal noninvestment classification is declared, not silently inferred from the tax exemption of an HSA trust. Legal character/eligibility and historical state basis are not established by this switch.

NJ fractions apply to the **entire actual funded withdrawal**, independently of federal receipt matching. They are conditional proportional recognition assumptions, not a reconstruction of NJ basis. Zero and one are explicit choices, and intermediate fractions support supplied illustrations. Unknown order references, missing required fractions or unconfirmed duplicate-tax context are rejected. A fraction cannot exceed one. An optional supplied fraction on a qualified-only order is also independent of federal qualification.

The HSA book transfers cash to the existing household wallet once. Its recognition event has zero cash and adds the computed positive federal taxable amount, separate additional tax and conditional NJ amount to the actual annual return. Existing employer funding, bank interest, personal deductions and payment priority are unchanged. Annual audit includes distribution ingredients and the source classification/fractions. Net wealth includes remaining HSA assets once and reflects actual paid or unpaid taxes; no hypothetical tax-saving deposit is generated.

## UI and checks

The household UI offers a synthetic nonqualified HSA case and editable source assumptions. Qualified reimbursements, nonqualified federal income, additional tax, conditional NJ income and unfilled requests appear separately. Existing qualified-only scenarios retain their defaults/results; advanced nonqualified use requires the new confirmations.

Independent cases verify:

- With only $3,000 in the HSA against a $5,000 request, actual federal income is $3,000, additional tax is $600 and an assumed NJ fraction0.5 recognizes $1,500. Starting household assets$103,000 end at$102,400 after the actual tax; the unfilled$2,000 is not taxable or a second cash receipt.
- A $5,000 funded withdrawal using $2,000 of qualified historical receipts leaves $3,000 federal nonqualified income. An independent NJ fraction0.5 recognizes $2,500 of the whole funded amount. The paid receipt cannot be reused.
- Actual dates straddling the supplied65th birthday, and supplied disability dates, change additional tax while retaining ordinary income.
- The declared noninvestment case with $300,000 wages, $30,000 interest and a $10,000 HSA withdrawal has AGI$340,000, NIIT$1,140 and additional Medicare$450. Actual external tax-event receipts remain$330,000, while the HSA asset transfer occurs once.
- The combined IRA illustration raises first-year contribution MAGI from$86,000 to$96,000 and federal AGI from$83,000 to$93,000. Payroll is unchanged; the $10,000 withdrawal adds $1,200 ordinary tax plus $2,000 additional tax, changing household ending wealth from$155,243 to$152,043.
- Existing qualified household totals remain unchanged, including shared receipts, combined IRA eligibility and actual tax/cash conservation. The real UI submits both profiles.

## Authorities and limits, checked October24,2026

[IRS Form8889 instructions (2025)](https://www.irs.gov/instructions/i8889) and [Publication969 (2025)](https://www.irs.gov/publications/p969) support nonqualified gross-income inclusion and the separate additional tax/exception ingredients. Those ingredients were already implemented in the standalone HSA engine and are now connected to actual household recognition.

The current [26CFR1.1411-3](https://www.ecfr.gov/current/title-26/section-1.1411-3) distinguishes exempt accounts and trust-beneficiary investment-income character. Its trust exemption alone is not used here as proof of every recipient's treatment. The [2012 proposed-regulation preamble, pp.72622–72623](https://www.govinfo.gov/content/pkg/FR-2012-12-05/pdf/2012-29238.pdf) explicitly discusses taxable HSA distributions, but proposed language is background rather than substituted current authority. This bounded profile therefore keeps noninvestment classification explicit. A current NJ withdrawal/basis conclusion was not established from the general insurance-plan sources located; state recognition remains an explicit independent input. Do not generalize this cash-bank profile to invested HSAs or claim issue6 complete.
