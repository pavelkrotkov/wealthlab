# Actual household policy funding and protection

A fully funded illustration cannot establish that a household can pay its premiums. This adapter executes the supplied policy events against the existing household wallet and annual federal/NJ return. It reuses the contract book from [ADR0102](0102-whole-life-contract-cash-and-tax.md), rather than constructing another tax or insurance valuation engine.

## Inputs and boundaries

Each policy has one USD insurance account, one named member owner, opening net surrender equity, an explicit federal contract profile, independent NJ event recognition and complete post-event monthly values. Its opening account equals gross surrender value less the actual policy loan. Generic contributions and account fees cannot bypass the policy ledger. The caller confirms that other income, expense and tax inputs exclude the policy's cash flows.

Every required outflow inside the household horizon needs a supplied terminal settlement that is explicitly confirmed to apply if that payment cannot be made. The program does not invent a grace period, automatic premium loan, paid-up conversion, insurer quote or continued death protection after a failed payment. Unsupported discharge amounts and unresolved tax terms stop the projection. The failure settlement is a conditional assumption, not an instruction to surrender a policy.

Monthly values must correspond to the chosen funded path. They remain supplied values on market simulations; securities and other explicitly bound assets follow the shared realized market paths. Missing values, unconfirmed qualification or an incomplete payment calendar cannot produce a household success conclusion. Insurance need is supplied independently for each owner and aggregated across that owner's policies.

## Cash execution

Within the policy adapter, dated events execute across all holdings in date order. Each cash/tax event is yielded to the shared tax ledger before the next policy payment is considered. Earlier actual receipts can therefore fund later policy events without duplicating cash or recognition. Existing monthly household receipt conventions and the ordered product hooks still apply; this is not a daily household settlement engine.

Cash-only funding uses available household cash. Permitted-sale funding calls the existing taxable-account/lot solver with the current tax, withholding, ordinary spending and required policy payment context. No permission to sell is inferred from a balance or wrapper. These sales are actual transactions: if all available permitted sales still cannot fund the payment, they remain executed and the payment fails. The policy payment itself is all-or-nothing. A failure executes its supplied settlement, retains the missed-payment funding failure and cancels later policy events and values.

Policy loans create cash and debt. Principal repayments consume cash without adding premium basis. Net surrender equity is the living household asset, already reduced by the loan; policy debt is not deducted twice. Death benefit is reported separately from living wealth. Actual source withholding reduces received cash and credits the same return once. Refunds remain receivables until their existing dated settlement.

## Reserve and retirement reporting

The policy reserve sums listed required payments over the configured forward reserve window (365.25 days per reserve year, rounded up to a day). It is added to the existing household spending/tax reserve. A lump premium or an unpaid terminal premium is never multiplied by twelve. The supplied payment calendar must be complete through the household end plus that reserve window. After termination, no future policy reserve or illustrated death protection remains.

The UI reports actual premiums paid after the owner's retirement date, remaining listed premiums after retirement, policy payment shortfalls, outstanding loan/basis, net cash/surrender/death values and uncovered insurance need. The separate illustration UI retains the timing-based return calculations. Changing a stop-funding date still requires values consistent with that changed path.

## Verification

Synthetic checks reconcile cash, shares, policy equity, actual tax and withheld refunds independently. A $50,000 cash household pays $2,000 premiums and $3,000 spending, receives a $500 loan and finishes with $45,500 cash plus $11,500 net policy equity. A MEC variant has $50 additional tax; paying it now or carrying it as a liability gives the same $56,950 after-tax wealth. Permitted lot sales, locked assets, failed-payment exits, cross-policy receipt ordering, all four market modes and the native Household form are exercised.

The matched liquid-saving and separately priced protection comparison remains a subsequent layer of issue14. This adapter does not assert insurer solvency, policy eligibility, suitability or a complete tax profile for every possible policy contract.
