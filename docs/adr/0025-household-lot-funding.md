# ADR 0025: Actual taxable lots fund household obligations

Status: a household/lot integration layer of open market ticket #8. Extends the [lot ledger](0004-lots-and-harvesting.md) and [household cash/tax conventions](0003-tax-cash-flow.md). Market-path binding, automatic harvesting/sale policies, distributions/fees, retirement replacement lots and January/prior-return wash reconciliation remain required follow-up work.

## One account value and one seller

A linked plan contains the complete taxable trading book, opening marks, ordered monthly closing marks and explicit account/security sale permissions. Dates match the household horizon. Owners map to the filing people; USD taxable wrappers and zero generic account fees must agree. Each household opening value equals the linked shares plus brokerage cash. Final marks match the lot case. There is no extra balance, duplicate position or inferred price filling.

Every linked account must be removed from the proportional-basis funding adapter. Generic transfers into linked accounts are rejected: share purchases belong in the trade book. Unlinked accounts may retain the older explicit proportional-basis convention; linked sources execute first in their supplied order. FIFO/HIFO selection uses the existing liquid-share selector, including acquisition/liquidity dates and stable tie breaks.

## Cash chronology and actual tax funding

The household still uses monthly cash settlement. Current ordinary income and dated receipts arrive before the linked book's manual trades. Those trades retain their actual dated/list order. A buy uses its brokerage cash or received household cash; insufficient funds block the case rather than borrowing from later wages or future sales. Remaining brokerage cash sweeps to household cash once. The linked wallet value then contains marked shares, not the transferred cash again.

After these receipts, assessed prior-tax arrears are paid before optional HSA/529/IRA deposits. This also corrects the previous receipt ordering, where a newly dated tax-event receipt could bypass the first arrears payment and fund an optional deposit. A real HSA/tax-ledger regression fixes that ordering contract. Current withholding/settlement and ordinary spending retain their existing priorities.

For a funding sale, copied trials use the same actual lot selector, microshare rounding, commission, holding periods, separate federal/NJ bases and wash books as execution. The existing funding solver evaluates the resulting current cash tax obligation. Only the chosen trade mutates holdings, transfers net sale cash once and updates the shared annual tax case. A feasible result may retain extra cents from microshare rounding; it is not a minimum-tax or global liquidation optimum. Explicitly permitted other accounts can fund any remaining gap.

Monthly closing marks value unsold shares. Gains are recognized from disposals, not market appreciation. Current tax payments use the resulting actual case; no annual comparison or estimated tax saving is deposited as cash. Unpaid spending/taxes remain visible even when illiquid shares leave positive wealth. The audit preserves actual remaining lots/bases, disposals, orders, funding cash, commissions, annual recognition and closing values. Unrealized gains remain in marked terminal wealth.

## Wash timing and bounded initial profile

The profile requires federal wash tracking, complete opening/outside-purchase context and an explicit NJ choice. Complete ownership and monthly timing/cash sweep need user confirmation. NJ no-wash or federal-rule mechanics remain conditional assumptions, not an inferred legal conclusion. Recognized NJ disposition losses remain in that category; they do not reduce wages.

As observations arrive, the actual book recalculates current-year wash-adjusted totals and adds only the recognition change to the household return. Unresolved forward-window losses remain excluded. A later qualifying purchase adjusts the actual replacement basis. A loss whose window expires in-year then becomes recognized in that same tax year. None of these basis/recognition changes creates cash.

An unresolved December window cannot simply become next-year income or an assumed refund. This initial profile blocks year-end pending losses until a January/prior-return reconciliation adapter can update the original tax year, payments/carries and completed wrapper eligibility correctly. It does not claim complete December harvesting support. Likewise standalone sale/harvest policies, distributions, fees, terminal exits and wrapper lots cannot be silently combined with this profile; their adapters remain unfinished. The existing standalone workbench retains those separate capabilities.

## Executed checks

The independently synthetic two-year household opens with $101,000, receives $60,000 wages, spends $120,000, pays $8,872 tax and $22 commission. Only unsold shares receive the second year's 30% price increase. Actual HIFO sales transfer $67,872 and leave $59,831.70 of shares. Federal/NJ realized gains differ because their bases differ. Moving the opening $1,000 between household and brokerage cash preserves every ending dollar.

Checks cover capital conservation, unchanged low-basis lots, exact separate basis/gains, no double proceeds, explicit liquidity and permission failures, no future-cash purchases, opening/owner/mark/seller guards, immutable JSON round trips, in-year pending/replacement losses, blocked December windows, actual sale gains removing Roth eligibility, arrears priority and real UI submission. This integration adds no new tax-law rule; existing source references in the lot/tax ADRs remain authoritative for their implemented policy versions.
