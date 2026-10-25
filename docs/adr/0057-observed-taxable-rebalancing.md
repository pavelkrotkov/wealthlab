# 0057: Taxable rebalancing uses actual sale proceeds and observed marks

Status: further integration of market issue #8. Extends the existing household
lot and sale/harvest ledgers without another trade, basis or tax engine.

A `HouseholdLots.rebalances` entry supplies a month-end date, account, complete
security target weights, drift band, maximum gross-sale fraction, FIFO/HIFO
selection and per-trade commission. Targets sum exactly to one and include
explicit zero weights for securities intended to be sold completely. Known
later manual purchases, harvest replacements and positive targets of earlier
rebalance decisions require target entries too. Earlier zero-weight targets alone
do not establish a potential purchase.
The schedule is ordered by date/account, once per account per date.

Weights refer to securities in the chosen account. They exclude cash, other
accounts and hypothetical after-tax liquidation values. At the decision date,
current marked security values fix both target dollars and the gross-sale cap.
A maximum weight deviation greater than the drift band triggers the decision.
Overweights sell in stable security-ID order, limited by actual liquid lots,
market locks, the sale cap and commissions. The cap measures one-way gross
sales; it does not include the subsequent purchases in its numerator. The
remaining sale budget floors to cents before sizing shares, and executed gross
reduces that budget using the same cent settlement as the cash book. Rounding
cannot exceed a fractional-cent cap.

Only cash raised by these sales can finance the resulting purchases. Existing
brokerage cash and household salary/reserves are not automatic top-ups. After
reserving each eligible purchase commission, available proceeds are allocated
proportionally to remaining positive target-dollar gaps. Purchases round down
to the existing six-decimal share precision and whole-cent budgets. Locked
purchases, tiny budgets or share precision may leave cash unspent. The normal
household sweep moves that residual cash once. Zero holdings or an unexecutable
decision cannot create a trade or a cash receipt.

Manual trades run first, existing sales and harvesting next, then rebalancing,
then the single cash sweep and actual tax-recognition delta. Every rebalance
trade uses the existing lot selection, independent federal/NJ bases, commission
capitalization and wash matching. A rebalance purchase can defer a previously
harvested loss; there is no artificial exemption for automatic policies.
Subsequent household spending and tax funding may sell more shares and alter
the allocation. This policy is not a tax-budget optimizer or a permanent
household concentration constraint.

The audit shows actual trade IDs, gross sales/purchases, commissions, residual
cash, observed weights before/after, pre-cost target dollars, remaining target
gaps and locks. A completed execution does not assert exact target attainment.
The same observations work in entered-price and all four generated market modes.
No subsequent mark is consulted to decide a current trade.

Markets / Household funding / **Taxable rebalancing** supplies a synthetic
quarterly equity/bond case. The optional matched buy-and-hold control removes
only the rebalance schedule: both policies keep the same initial assets,
spending, taxes, liquidation permissions and immutable market batch. The control
still sells assets when actual household funding requires it. Editable JSON
supports other targets, dates, costs and caps. Historical starter observations
are invented, and the two-year example cannot establish retirement safety.

Independent numerical checks include a $1,000 position with $100 federal and
$200 NJ basis: a zero-cost 50/50 rebalance realizes $450/$400 gains and buys
$500 of the other security. Two $1 commissions leave $500 in original shares,
$498 in new shares and $499 new tax basis. Existing $777 brokerage cash remains
untouched by the purchase. A 10% sale cap leaves 90/10 weights. A repurchase
within 30 days defers an actual $500 federal loss into replacement basis while
preserving the explicitly different NJ wash assumption. Further checks cover
locked targets, share rounding, identifier bounds, all market methods, UI and
unchanged earlier cash/trades after a last-month crash.
