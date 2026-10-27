# ADR 0077: Actual QOF assets on shared household paths

Status: bounded market adapter for issues [12](https://github.com/pavelkrotkov/wealthlab/issues/12) and [18](https://github.com/pavelkrotkov/wealthlab/issues/18), retaining [the native QOF contract](0062-qoz-source-gain-contracts.md) and [source-year revision machinery](0063-qoz-prior-source-returns.md).

## Native execution owns capital and tax

An explicit `HouseholdBinding.qoz` names the whole native account and one asset factor. The source description and confirmations state that the factor is net of entity-level tax, before native financing, manager fees, investor costs, dividends and carry. Every generated cash yield for this factor must be zero: supplied ordinary dividends remain actual separate distributions in the native book. This convention does not invent QOF performance history or classify a different legal structure.

The compiler changes only dated asset returns and sets each dealing lock to the logical OR of the supplied lock and the realized factor lock. It retains dividend observations, source identities, calls, tax elections, financing, costs, carry and settlement terms. Complete native month-end coverage, accepted-subscription dates and tax/exit clocks remain required. Direct market `Execution` also verifies the exact compiled observations, so a caller cannot silently execute stale supplied returns against another realized path.

The original starter replaces its illustrative fixed-price source trade with a native dated `sell_all` policy. Its policy ID is the call's source trade ID. Household execution supplies the actual observed stock price and generates the actual disposal row. General user inputs are never rewritten into a qualifying disposal. Missing, blocked or ambiguous source rows fail through the native QOZ source guard; manual fixed-price trades remain unsupported in market runs. No future source gain or forecast tax refund funds a call.

Existing ordering remains observed asset returns, actual source sale and cash sweep, funded calls, ordinary dividends, statutory inclusion/sale and due settlement. New call capital earns no already observed call-month return. A dealing lock may defer a sale or cash distribution without deleting value or postponing statutory inclusion. A locked subscription needs a separate pending-investment model and is rejected.

## Observable exposure and UI

The native household summary exports actual creditor-book long assets as `qoz_entity_asset_value`. Factor exposure uses that gross asset amount, while the shareholder account retains NAV and actual settlement receivables. Internal debt is neither erased nor subtracted twice from household wealth. Underlying issuer inventory remains unknown; a factor proxy does not establish issuer diversification.

Markets / Household funding / **Opportunity-zone household** exposes editable household, market and binding JSON and the existing identical-batch comparison workflow. Results show source/factor identity, actual calls, gross assets, NAV, debt, dividends, inclusion and settlement alongside household cash and tax outcomes. The historical-mode starter is explicitly original invented mathematical factors, not actual market or QOF observations. Real historical replay still requires complete supplied source and availability metadata.

## Independent checks and limits

An original unlevered 2026 example starts with $100,000 stock plus $5,000 cash and receives $72,000 wages. A native sale produces $80,000 federal / $70,000 NJ source gain. Its $80,000 call and flat December settlement conserve capital; federal income tax $7,953, payroll $5,508 and NJ $4,960 leave $158,579 actual cash/wealth. A post-call $8,000 asset gain uses the actual QOF-stock holding period and leaves $163,977 after $21,023 tax. A call-month return earns no benefit on unfunded capital. A December lock leaves the $80,000 stock NAV and $78,579 cash while inclusion still occurs; January unlock deposits the proceeds once. A 1.3-times exposure maps $104,000 assets and $24,000 internal debt separately from $80,000 shareholder NAV.

The adapter makes no new legal determination. Native opening-interest, pass-through, source-year, conditional-election, settlement and future-tax assumptions remain visible. It does not add optimizer controls, synthesize underlying issuer holdings, repair absent source facts or support pending subscriptions. The native authorities and tax classifications in ADR0062/0063 remain unchanged.
