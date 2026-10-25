# 0064: Dated foreign-tax cash feeds native federal credits

Status: first vertical of cross-border issue #17, not completion of moves or
household foreign-tax execution. Reuses the existing annual federal/NJ engines,
Tax-Calculator6.8.5 and typed money; no dependency or second US tax engine.

## Credit order and actual cash

`AnnualCase.foreign_credits` holds independently permitted regular and AMT
credits with allowed/denied/unresolved eligibility and provenance. Regular FTC
enters native `e07300`; AMT FTC enters `e62900`. Explicit `f6251=1` with an
allowed claim prevents the package's no-Form6251 shortcut from silently treating
regular FTC as AMT FTC. This selects a numerical computation, not a filed form.
An oversized regular claim rejects. Native nonrefundable-credit order, NIIT,
payroll, original payments and independent NJ liability remain in their existing
engines. Supplied eligibility is not a legal determination.

The Cross-border workbench edits one dated annual filing unit: stable people,
recognized source income, actual tax payments/withholding/refunds, explicit
USD-per-native-unit spot quotes and opening credit vintages. Source amounts
reconcile exactly to worldwide ordinary federal facts. No source recognition
or credit deposits cash. Nonincome foreign taxes and conversion fees retain
their actual cash cost without becoming income-tax credits or deductions.

The foreign liability year is a historical identity, independent of the actual
paid-method US credit year. A prior foreign liability paid this year uses this
year's supported source limit; a prior paid year needs its own carry context
and is never silently shifted forward.

A refund identifies the original taxpayer/payment, currency, jurisdiction,
basket and liability year. Its cash uses the receipt-date quote while credit
reversal uses original-payment FX. Independent native cash and credit caps
prevent over-reversal. A positive refund currency difference requires a
separately supplied, recognized ordinary-income row with matching owner,
date and amount; this does not infer its legal source or create another cash
receipt. Unknown or negative currency-income treatment blocks the profile.

## Bounded calculation and unresolved positions

The derived credit profile uses final2025 ordinary general/passive income and
standard-deduction source apportionment, with explicitly confirmed income/tax
allocations and prelimited creditable foreign income tax. Later years require
an explicitly frozen2025 policy. Each basket has its own source limit. Current
paid tax uses capacity before original opening vintages, oldest first; vintage
age never resets. Generated excess reports its origin and ten-year expiry.
Unreviewed prior-year carryback capacity and joint-person allocation remain
explicit; no prior refund is assumed. Opening carry use requires confirmed
person/filing continuity. This is not a full Form1116 filing implementation.

Preferential income, retirement/business/excluded income, losses, itemization,
special deductions, unresolved classifications, treaty resourcing, passive
high-tax/special reclassification (a passive category requires independent
confirmation that none is needed), and a
computed/induced AMT need further profiles. Original-year foreign refunds
remain blocked until the closed-return consumer performs redetermination.
Unknown facts show actual observed tax cash and baseline liability while
withholding the affected candidate, rather than selecting a favorable zero.
The lower workbench does not determine residence, Spanish/PR tax, NJ departure,
foreign assessment payment, source withholding funding or household safety.
Those require the later person/jurisdiction and shared cash-execution layers.

## Primary evidence and independent checks

QMD tax-reference discovery preceded official passage checks on October25,2026.
The [2025 Form1116 instructions](https://www.irs.gov/instructions/i1116),
particularly separate categories, paid/accrued taxes, PartI allocation and
PartIII limits/carryovers, define the effective-year boundary. The official
[2025 Form6251 page1, lines5–11](https://www.irs.gov/pub/irs-pdf/f6251.pdf)
was visually checked: independent AMT FTC precedes tentative minimum tax;
regular FTC also affects the regular-tax comparison.
[IRC986(a)](https://uscode.house.gov/us/usc/119-120/t26/s986/) supports separate
credit FX, and [Treas.Reg1.905-3](https://www.ecfr.gov/current/title-26/section-1.905-3)
requires original-year redetermination for relevant later adjustments.
The final2025 forms are not proof of later-year amendments. Govinfo's retrieved
[904](https://www.govinfo.gov/link/uscode/26/904) and
[905](https://www.govinfo.gov/link/uscode/26/905) snapshots were2024 editions;
applicability beyond this frozen/final2025 profile needs a current-year check.

Independent brackets give $13,449 ordinary federal tax for a single age40
person with $100,000 wages and $15,750 standard deduction. Half foreign-source
income gives a $6,724.50 limit; an actual EUR10,000 payment at1.10 costs
$11,000 and leaves $4,275.50 excess, without predicted refund cash. A EUR1,000
refund at1.40 returns $1,400 but reverses $1,100 credit tax, leaving a separate
$300 currency-income question. The Form6251 controls give $3,094 tentative
minimum tax on $100,000 ordinary AMTI and $42,094 on $250,000; regular FTC
cannot erase these without independently supplied AMT FTC. Checks also cover
NIIT/payroll separation, vintage expiry, independent basket capacity, denied
versus unknown credit with identical cash, malformed ownership/FX/source data,
nonincome tax/fees and real editable UI submission/export/stale-result removal.
