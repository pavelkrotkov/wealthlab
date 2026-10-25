# 0049: Realized market paths consume the workplace RMD ledger

Status: accepted. Depends on [complete-plan RMD accounting](0048-workplace-rmd.md).

## Result

Markets / Household funding adds **Workplace RMDs** with editable household,
market and explicit account bindings. The existing deterministic, historical,
correlated Monte Carlo and named stress generators supply the same monthly
marks, yield and outgoing locks to the workplace book. The consumer adds no
second RMD, cash or tax algorithm and never uses later prices for earlier
withdrawals. Each January target uses actual preceding December marks.

Per-path outcomes report required totals across years, total original-year
shortfalls, excise tax, terminal unresolved requirements and the first failed
RMD month. These remain distinct from unmet spending cash: a required withdrawal
is an internal transfer, not another expense deducted from wealth. Missing a
required distribution fails the existing household funding assessment, including
under a contingent zero-excise assumption. Prior missed requirements remain
unresolved under the documented adapter boundary rather than disappearing when
the next year starts. Failure dates identify monthly periods, not legal due dates.

The actual Markets UI includes the same per-plan target/payment/excise table,
source-withholding and account audits. Paired alternatives reuse one realized
batch and identical indices; a policy can change December catch-up without
regenerating more favorable returns. All annual tax, source credit, refund-date
and rule-scope limits from the household ledger remain applicable.

## Evidence and limits

Seven new checks execute all four path methods, a whole-horizon illiquidity
stress, a matched catch-up comparison and the submitted Markets form. They
verify original-year requirements, gross/net cash, failure timing/magnitude,
source credits and capital reconciliation. For the synthetic zero-spending
case, ending wealth equals $492,000 opening assets plus actual investment change
minus reported tax liability. Actual source-paid credits are not deposited as
market returns or immediate tax-saving cash.

The illustration lasts two years. It does not establish funding through the
configured full retirement age, identify underlying issuers or calculate a
fully liquidated terminal after-tax exit. Market bindings explicitly represent
full-account factor proxies. The underlying RMD profile still requires eligible
ordinary vested zero-basis plan cash, confirmed groups/beneficiaries and source
separation by December1 in RMD years. Current-employer delay, first-April
deferral, actual prior shortfall corrections, broader workplace basis, Roth
plan withdrawals and rollovers remain unfinished retirement work. Market
rebalancing and the bounded optimizer remain separate open tickets.
