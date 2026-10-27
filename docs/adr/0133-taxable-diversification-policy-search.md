# Taxable saving allocations and observed rebalancing in policy search

The bounded optimizer can replace native taxable saving and rebalancing schedules as independently lockable policy dimensions. `null` preserves the baseline schedule; `[]` clears it. The existing sale/harvest, account, retirement and spending controls can be combined with these schedules. All candidates still start with the same accounts, lots, basis, income and tax facts, and run on one common training batch before frozen-policy validation.

A saving policy sets a dated cash budget, target weights and minimum cash buffer. The existing saving adapter reserves required bills and tax, buys actual shares with available cash, pays commissions and returns unused amounts. A rebalance uses current observed marks, an explicit drift band and sale cap, then reinvests only its own sale proceeds. It cannot borrow from household cash or rewrite original positions to the target weights. Partial execution, share rounding, costs and liquidity locks leave visible residual drift.

The native books enforce target coverage and weights, dated execution, funded purchases, federal/NJ basis, wash recognition and terminal disposal. Controlled saving and rebalance schedules retain common per-trade commission assumptions for each account across baseline and all choices. The foundation guard likewise keeps sale/harvest execution terms and explicit IRA exception facts shared. Costs vary with actual executed trades, not a favorable fee assumption chosen by the search.

## Synthetic UI and independent cash identities

Optimize offers a stock/bond diversification starter, combinable with account policies and robustness checks. It compares stock-only saving, a bond completion purchase and a stock/bond rebalance with split saving. The example adds one explicitly assumed independent bond factor to training, validation and every named check. Historical bond observations are invented zeros and labelled synthetic; they are not provider data. Existing equity/inflation dependence is retained. The default age-100 horizon and concentration requirements remain unchanged.

In the flat-price, full-basis check, all candidates start with $300,000 and spend $48,000. Stock-only saving pays $2 of commissions and ends with $251,998; balanced reallocation and split saving pay $6 and end with $251,994; a bond completion purchase pays $3 and ends with $251,997. The balanced trade sells $50,000, spends $49,998 buying bonds and pays $2 commissions without a wallet top-up. The remaining allocation drift is reported. Late saving after the final sale reopens holdings and prevents a completed-exit ranking.

## Final annual tax status

The real balanced case exposed a reporting error: an intrayear pending wash window kept its whole year labelled provisional after the native book had finalized it. Annual reporting now uses each year's latest observed provisional status, matching how it selects annual tax results. A later calendar year's ordinary row cannot clear an unresolved prior return; an actual recorded revision remains necessary. This changes reporting/eligibility, not tax calculations or historical cash. Regression checks retain January revision/refund timing, partial-year labels and unresolved prior-year flags.

Checks cover actual capital/cost/basis preservation, residual drift, reopened positions, missing books, invalid weights, shared commissions, synthetic-history provenance, native UI, account integration and frozen robustness. Product-specific blending/exits, employer-compensation closure and cross-border optimization remain required for issue18.
