# Matched insurance and liquid-saving alternatives

Whole-life policy schedules can now be compared with liquid saving and independently priced term protection through the same household projection. This completes the comparison calculation/UI part of issue14; publication, current-head review and CI are separate gates. The actual policy cash/tax and household adapters remain those in [ADR0102](0102-whole-life-contract-cash-and-tax.md) and [ADR0103](0103-household-whole-life-funding.md).

## Matched financial background

Each alternative is a complete editable household scenario. Horizon, members, income, spending, debts, tax assumptions and other product plans must match. Non-insurance accounts and their opening capital are identical. Linked lot books, opening bases, observations and sale permissions are identical; only the optional saving schedules may differ. Every alternative uses the same independent insurance needs.

New zero-cost insurance accounts may differ. Existing policies must carry the same opening loans, cost, gross values and contract tax profile across alternatives, including fully loaned or zero-surrender-equity policies. The liquid reference must execute an explicitly supplied opening surrender/lapse for each existing investment policy. Its gross settlement must equal the supplied opening surrender quote; debt satisfaction happens before actual cash is available. The existing contract book recognizes any taxable gain and additional tax. Replacing a policy account with cash without executing that settlement is rejected.

Term protection uses the existing policy ledger with independently supplied premiums, zero cash/surrender values and no loans or investment receipts. Its required-payment failure settlements must also have zero value. Death coverage, termination after an unfunded premium and future premiums are explicit supplied schedules. No premium quote, underwriting result, policy guarantee, dividend rate or continuation right is inferred. Insurance need remains independent of investment wealth.

## Actual optional saving

A saving instruction specifies an observed month-end date, actual taxable account, target security weights, total cash budget including commissions, and a minimum cash balance for that decision. It follows product cash events and precedes optional wrapper deposits. It reserves current modeled household bills, the existing annual-return cash-tax quote and that specified buffer. It neither sells assets to finance itself nor borrows money.

Purchases reuse the live lot book, generated trade IDs, share rounding, commissions, federal/NJ bases and wash-sale recognition. Locked securities are not purchased; their allocation stays in cash rather than being redistributed automatically. Unspent rounding/commission amounts also return to household cash. New purchases can change wash recognition; the normal final tax-funding pass observes that change. The cash buffer governs this saving decision, not unrelated later withdrawals, other optional deposits or a global reserve guarantee.

Saving budgets can remain partially or entirely unfilled without creating a mandatory-spending failure. Actual invested cash, commissions and unfilled amounts are separate reported quantities. The existing household reserve calculation and actual required-payment failures remain visible. Different limited-pay and longer-duration schedules may leave different liquidity and premium commitments; equal opening capital does not imply equal risk or protection.

## Market pairing and UI

Entered observations and all four shared market methods use the same household engine. Generated comparisons create one realized batch and reuse it for every alternative and path index. Actual purchases use the observed monthly prices; future shocks cannot change earlier orders. Supplied policy values remain conditional schedules, not simulated insurer guarantees. Historical starter data is explicitly synthetic.

Products / Whole life versus liquid saving imports and edits all alternatives, term prices, saving budgets and shared market inputs. It displays funding failures, cash-reserve breaches, protection gaps, retirement premiums, actual tax payments and marked wealth. Inputs, complete audits, outcomes CSV and individual Household scenarios can be exported. Household also exposes a synthetic scheduled-saving example and the actual trade audit.

Marked wealth deducts recognized tax liabilities. Unexecuted future exit taxes remain excluded, and death protection is never added to living wealth. This view does not automatically rank strategies or present marked wealth as a fully liquidated after-tax result. Existing supplied terminal policy events and dated sell-all policies can be entered to model actual exits; their resulting cash, recognized taxes and remaining assets are auditable. Short examples cannot establish funding through age100.

## Independent checks

Flat-market new-policy cases start with $10,000 and spend $3,000. The supplied limited-premium path ends with $7,000 living wealth, while $300 separately priced term premiums leave $6,700. The reference purchases $1,800 actual shares and retains $4,900 cash; its $150,000 protection stays separate from wealth. The policy's smaller protection leaves an explicit gap.

An existing-policy case starts with $50,000 cash and $10,000 policy equity. Supplied MEC basis of $5,000 produces $5,000 surrender income and conditional $500 additional tax; the retain path's later $500 loan produces conditional $50 additional tax. A separate $8,000 opening-loan variant receives only $2,000 surrender cash without changing the $5,000 gain. Other checks cover cash floors/tax reserves, actual wash basis, commissions, market locks, future-path independence, all four market methods, matched-input rejection and native editable UI behavior.
