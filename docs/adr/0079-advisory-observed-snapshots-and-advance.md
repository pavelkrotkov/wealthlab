# ADR 0079: Observed advisory valuation snapshots and bounded advance bills

Status: dependent extension of [ADR0078](0078-household-outer-advisory-fees.md) for [issue #18](https://github.com/pavelkrotkov/wealthlab/issues/18). This implements its tracked opening/advance task for an explicit monthly billing cutoff; it does not infer a named adviser's terms.

## Actual observations have a date and a cutoff

An explicit snapshot plan names `valuation_timing="explicit_observed_snapshot_cutoffs"`. Each period separately names its valuation date/cutoff, accrual start/end (end exclusive), assessment date and payment due date. The cutoffs are `opening`, `completed_month_end`, and `product_marks_before_optional_saving`. The initial same-date product-stage profile remains compatible.

The projection captures opening state before current-month income, compensation, IRA movements and market execution. It captures completed state after actual monthly transfers, taxes, fees and spending. The fee book captures its product stage after native product marks/receipts and before optional saving. Two observations on the same calendar date are not interchangeable. A completed observation on the current billing date does not exist yet at the earlier product stage and therefore fails explicitly. Previously executed product-stage snapshots can also be retained when requested.

The cache stores only requested date/cutoff/account combinations as execution actually reaches them. It never fills a missing past date from a future supplied scenario mark or infers a pre-projection observation. All simultaneous schedules resolve immutable recorded values before any current fee payment. Source-confirmed absent optional accounts remain explicit zero covered AUM, with fixed charges still governed by the supplied contract.

Opening and completed snapshots permit native HSA/529 account bases that are unavailable at the earlier current product stage. Actual unpaid HSA custody debt is subtracted per account from the positive fee base; native asset balances and the separate household liability are preserved. Paid fees are already absent from native cash and are not subtracted again. Net AUM is floored at zero while the actual debt remains owed in its original book. Life opening cash/surrender values use the supplied opening values less the actual opening loan. Later life snapshots use executed native values, excluding death protection. Employer contingent/unvested rights remain outside account equity.

## Monthly advance billing without backdated cash

Assessment and contractual due dates remain actual modeled month ends. The existing monthly cash convention can use receipts realized within that month; actual payments are recorded at its end. A contract requiring first-day/daily payment, another due date, or an unavailable valuation cutoff remains unsupported. A January 31 payment is never relabeled January 1.

A full future accrual span is permitted only with the separate source-confirmed nonrefundable/no-proration assumption. Unknown refund, cancellation or proration rights are not fabricated. The entire supplied span must fit inside the modeled horizon. The fee source and availability must precede both the first accrual start and the first actual assessment, so a quote learned at a future service date cannot create an earlier bill.

For example, a January 31 invoice can charge the full February 1–May 1 interval using the actual January 1 opening snapshot. At $100,000 AUM, 1%, 89 actual days/360, it assesses $247.22. If January has no available cash and no permitted funding, the bill remains owed. A February receipt can pay it only on the actual February 28 payment row. No forecast receipt, advance tax deduction or new loan appears.

Existing marginal tiers, fixed charges, shared cash-pool validation, same-snapshot ordering, optional-deposit reservation and gross-cash required funding remain in the original ledger. This layer changes valuation-source selection and advance contract guards, not product cash, basis or tax recognition.

## UI and independent checks

Household offers an original observed-opening advance starter, with editable cutoff/accrual/contract fields. Markets offers the same advance profile on its existing shared realized batches. The invented monthly schedule covers services from the second modeled month through the horizon and explicitly charges no first-month service period; it is not an adviser quote or an assumed universal annual contract. Complete actual inputs and observed snapshots export with assessments and actual payments.

Independent original checks include the full 89-day/$247.22 advance invoice; $100,000 stored opening AUM unchanged by a current 10% move or future 50% shock; two schedules both observing $990 completed cash after an earlier $10 actual bill; and native HSA $10,000 gross assets less $250 unpaid custodian debt giving $9,750 net AUM and a $91 outer charge. HSA assets/debt/cash reconcile to $10,659 wealth. Native 529 opening $30,000 versus prior completed $33,000 remain distinct after a later 50% decline: fees are $25/$27.50 and wealth is $17,447.50. Opening policy loan debt changes the fee base without changing native policy basis or later loan cash. Actual first-day/future/unobserved snapshot and unknown-refund cases fail instead of receiving substitute values or dates.

First-day/daily execution remains a concrete unsupported timing profile. Whether a real adviser needs it requires actual supplied terms; this generic model does not infer billing frequency, advance/arrears status, refundable rights or valuation bases from a firm name. Optimizer scope/comparability and private source interpretation remain owned separately.
