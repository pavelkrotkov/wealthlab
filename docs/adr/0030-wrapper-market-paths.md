# ADR 0030: Ordinary IRA and 529 market-return proxies

Status: further integration for open retirement ticket #6 and market ticket #8. Reuses the existing chronological IRA/529 ledgers, actual household cash/tax recognition and realized market batches. No new dependency or tax-law rule.

## Explicit account proxies and timing

A wrapper binding explicitly maps an ordinary IRA or household 529 account to one market factor. It represents the entire account as that factor proxy; it is not an inferred inventory or a multi-asset holdings/rebalancing model. The user confirms replacing that account's entered return schedule. Compilation changes a copy, preserves unbound schedules, and retains the original household/binding/batch in exports. Duplicate bindings, unknown factors/accounts and unsupported wrapper plans block.

Each generated month-end `AccountReturn` applies the factor's full monthly mark change plus separately specified cash yield to the balance immediately before that event. Yield stays invested inside the wrapper; it is not deposited into household cash or separately recognized as taxable brokerage income. There is no multiplicative mark/yield cross term. Month-end deposits present before the return receive it; earlier dated withdrawals receive none of that later return. This is an explicit monthly planning convention, without daily interpolation or an issuer dividend calendar.

Generated rates retain twelve decimal places instead of the previous six-place manual-input ceiling. Existing cent-rounded return-change accounting remains authoritative. A fixed 2% monthly return compounds $100,000 to $126,824.17 and $30,000 to $38,047.26 under that ledger's monthly rounding. Their combined gain is $34,871.43. This differs by cents from rounding only a closed-form terminal value and is not a tax benefit.

Wrapper-only runs need no fictitious taxable account. Mixed taxable/wrapper runs share the same realized batch: only taxable opening holdings contribute market cash yield to household receipts and ordinary recognition. Bound wrappers use their existing withdrawal, conversion, basis, contribution and tuition rules; this layer does not create new tax eligibility or funding permissions.

## Outgoing liquidity restrictions

A dated `AccountLock` is a supplied, half-open `[start, end)` outgoing restriction. It is not a legal rule inferred from the wrapper. It retains account value and market returns, allows incoming deposits, and blocks source-account withdrawals/conversions. For 529s, an unfilled institution request may use actual household cash fallback; otherwise tuition remains unfunded. A restriction ending on an order's date no longer blocks it.

Restrictions are validated against known accounts and projection dates, require resolved provenance, and participate in record-ID uniqueness. Multi-year restrictions are clipped for each annual ledger without extending their original interval. Market factor locks generate corresponding outgoing account restrictions; user-entered restrictions are preserved. Required-withdrawal targets and reported shortfalls survive a lock. Existing excise/correction and broader retirement scope limits remain; an illiquidity scenario does not erase an RMD or establish a penalty exemption.

## Concentration coverage

Observed taxable issuer positions and whole-account factor exposures are reported separately. A wrapper proxy does not disclose its underlying issuers. Positive unobserved accounts make issuer concentration coverage incomplete; a wrapper-only result reports an unknown issuer weight rather than zero. Known factor values remain visible, as do positive accounts with no market-factor binding. Optimization must not treat incomplete issuer inventory as a satisfied concentration limit.

The existing market profile still requires explicit household taxes. Taxable holdings retain their price-plus-cash convention; a wrapper-only run may use a validated reinvested total-return factor whose separate yield is zero. HSA investments/NJ recognition, workplace holdings, employer returns/employment correlation, multi-asset wrapper holdings and broader funding policies remain separate required integrations.

## UI and executed checks

Markets / Household funding offers **IRA and education proxies** as an account scope. Its editable synthetic example shares fixed IRA withdrawals/conversion dates and qualified tuition with actual cash; factor exposures and incomplete issuer coverage are visible. Deterministic, Monte Carlo, supplied historical and named stress inputs use the same machinery.

Checks reconcile both exact ending balances with unchanged $100,000 household cash, replacement of an entered 50% return without mutating its source, a $200,000 early withdrawal funded only to its $100,000 available balance, locked spending/conversion failures despite positive marked wealth, retained RMD shortfalls, cash-funded versus unpaid locked tuition, half-open/cross-year restrictions, explicit mapping guards, mixed-account cash/tax recognition and the actual UI.
