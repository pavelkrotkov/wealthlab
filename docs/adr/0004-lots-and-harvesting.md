# ADR 0004: Tax lots and harvesting

Status: gross lot-accounting foundation implemented; wash adjustments, policies and household integration in progress under #5.

Lots carry quantity, acquisition date, federal holding start, liquidity date and separate total federal/NJ basis. Quantities are units, basis is a total dollar amount, and trade prices are per unit. Every account has explicit ownership and wrapper. The current workbench is long-only and USD-only; it does not interpret a retirement-account lot basis as a deductible IRA contribution or tax basis in distributions.

Opening positions must exist by the opening date. Trades run in supplied date order, preserving supplied order on the same day. Closing prices are explicit valuation assumptions. No price path, historical series or return process is inferred from trade prices. Unknown references, unresolved critical provenance, ID collisions and out-of-period trades block calculation.

FIFO orders by acquisition date; HIFO orders by federal basis per share, with stable date/ID tie breaks. Specific identification honors the supplied ordered lot list and rejects locked or mismatched lots. HIFO is a selection policy, not a determination that the broker accepted specific identification. Selection validates total availability before mutation. Partial sales allocate basis and net proceeds while retaining exact residual totals. Purchase commissions enter basis; sale commissions reduce proceeds. Purchases must be funded by that account's cash.

The UI currently reports gross realized gains, remaining lots, cash, transaction costs and marked gross wealth. It explicitly does not report recognized harvesting benefits or after-tax wealth. Retirement holdings, gains with different jurisdiction bases and loss trades can be inspected without inventing tax consequences.

## Next implementation constraints

Wash matching must consider the entire configured household, including spouse and IRA/Roth purchases, with explicit substantially-identical groups. Groups and replacement eligibility are assumptions; the program cannot infer legal identity from different tickers. Preserve share-level partial matches, replacement basis adjustments and holding-period carryover; IRA replacements must not receive a taxable-account basis increase. Track unresolved future wash windows without giving a decision policy access to future purchases or returns. A December loss and January replacement require original-year recognition, not a January capital loss.

Policies must distinguish fractions of original shares, portfolio-value concentration targets and economic exposure. Tax-budget decisions use the household tax engine and available information. A matched harvesting-off run shares prices, cash flows and fees. Gross losses, disallowed/deferred losses, recognized losses, own-gain use, external-gain offsets, carry and terminal liquidation must remain separate. Account sales that fund household obligations will eventually select actual lots instead of the tax layer's interim proportional-basis adapter; the two adapters must never dispose of the same account twice.

## Primary reference checks

Checked October 23, 2026. [IRS Publication 550 (2025), basis and wash-sale sections](https://www.irs.gov/publications/p550), supplies identification, calendar holding-period, partial replacement, spouse and basis rules. The local reference collection contains a 2024 Publication 550 snapshot; the current 2025 primary source was checked separately. [Revenue Ruling 2008-5](https://www.irs.gov/pub/irs-drop/rr-08-05.pdf) establishes loss denial for IRA/Roth replacements without increasing IRA basis. NJ basis and category recognition require separate treatment; no federal-conformity assumption is silently imposed by this gross-accounting foundation.
