# 0051: Actual workplace source assets fund direct ordinary IRA receipts

Status: accepted; part of open retirement ticket #6. Depends on the
[annual incoming receipt primitive](0050-incoming-ira-rollovers.md), with the
same dated primary references checked October24,2026 (New York).

## Result

Household adds **Load synthetic direct plan rollover**. Optional
`workplace_plan.cash_withdrawals.direct_rollovers` requests confirmed eligible
cash from a separated, fully vested ordinary pretax401(k) source with zero
federal/NJ basis. The target must be an explicitly classified same-owner
ordinary traditional IRA. Existing source access, complete-history, RMD-year,
liquidity and special-feature guards still apply. Complete calendar years,
first-day transfer dates and resolved input provenance are required.

These requests do not generate spending cash, source withholding, contribution
room, a deduction or taxable source income. Actual available source principal
limits the transfer; unavailable optional amounts remain auditable and are not
retried. A source debit creates exactly one funded incoming IRA receipt. The
household's initial assets must already include the source balance and exclude
any duplicate transfer receipt.

## Monthly chronology and RMD protection

When this adapter is enabled, first-day source cash orders and any elected
December catch-up run before direct transfers and IRA withdrawals. Their
existing net receipts and source-payment credits enter the tax ledger once at
the normal receipt stage. Employee payroll funding and remaining month-end plan
returns retain their existing position. A transfer cannot use later source
returns or silently fund a previously failed IRA order.

The source's complete plan group must have satisfied its current requirement in
actual cash before an eligible direct transfer. Unresolved prior requirements
from that same plan also block the request; another plan's excess, a new year's
cash payment or a contingent zero-excise assumption does not cure them. The
adapter does not infer a corrective filing or apply a proposed allocation rule.
Rollovers never satisfy an RMD. New IRA receipts do not inflate its opening
prior-December target; next year's target uses its actual closing value.

The IRA book uses its existing dynamic annual reconciliation even when there
are no ordinary contribution elections. Its cache key includes the count of
actual funded incoming receipts, avoiding stale precompiled balances. Only
known funded transfers enter the engine; scheduled future transfers do not.
Actual household-funded ordinary IRA deposits can coexist, with their separate
cash funding, room, completed compensation/MAGI and basis checks unchanged.
Completed basis carries into subsequent years. IRA cash withdrawals retain
IRA age/exception rules; the source plan's separation-age55 exception does not
follow a rollover.

## Evidence and limits

The synthetic household starts with $10,000 cash, a $100,000 source plan and a
$10,000 IRA. Its confirmed $80,000 February transfer leaves $20,000 in the plan
and $90,000 in the IRA, with cash still $10,000 and wealth $120,000. A later
$15,000 IRA withdrawal leaves $75,000 in the IRA and $25,000 cash before tax.
The55-year-old's IRA withdrawal has $1,500 additional tax despite the source's
age55 separation eligibility; final wealth is $118,500 in this illustration.

Checks exercise the submitted UI, same-day/earlier IRA draws, source shortfalls,
locks/no retry, separate source/destination returns, annual cache invalidation,
unchanged inputs, changing years, matching owner/product/IDs, actual per-plan
RMD ordering, persistent prior shortfalls and concurrent ordinary deposits.
With a separately cash-funded $3,000 deductible IRA deposit, the $80,000 receipt
still uses no ordinary contribution room; independent NJ basis recovers
$483.87 on the $15,000 draw and carries $2,516.13.

The UI shows funded value separately from spending receipts and lists source
locks, unmet requests and unresolved RMDs. It exports the complete audit and
annual reconciliation through the existing household files. Conditional tax
rules and tax-payment timing remain those of the underlying household ledger.
Nonzero source basis, source allocation, direct Roth conversion/designated Roth,
60-day/in-flight transfers, actual prior-RMD corrections and broader employer
benefits remain separate required profiles. This bounded adapter does not close
the retirement ticket or establish lifetime spending safety.
