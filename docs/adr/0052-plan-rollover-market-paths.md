# 0052: Realized plan and IRA paths share actual direct-transfer accounting

Status: accepted. Depends on [actual household source transfers](0051-household-plan-rollovers.md).

Markets / Household funding adds **Direct plan rollovers**. Its editable original
synthetic household, market and wrapper bindings run deterministic, historical,
correlated Monte Carlo or named stresses through the same actual source/IRA
ledger. Returns use each book's actual remaining month-end assets. A later
price cannot increase the earlier funded transfer, and source/IRA liquidity
restrictions remain independent explicit bindings.

Per-path outcomes expose actual funded rollover total, unfilled request total
and first unfilled date. These optional instructions remain distinct from
mandatory spending failure. Existing paired comparisons retain one realized
batch and path indices, with actual spending, taxes and wealth outcomes. The
selected path displays its source/target audit through the existing household
UI; input, batch and result exports retain reproduction data.

Seven new checks execute all four methods, the submitted Markets form, a matched
$80k-versus-$40k transfer comparison and whole-horizon illiquidity. The matched
example gives both wrappers the same factor and sufficient assets to pay the
same withdrawal: reallocating them creates no tax savings or wealth beyond
rounding. Across methods, original$120k capital plus actual source and IRA
investment change minus reported tax liability equals ending nominal wealth.
The built-in illiquidity stress blocks the actual request without retry or
invented destination assets. A realized batch is immutable; test scenarios
change the supplied stress rather than rewriting generated prices or locks.

This two-year example does not establish lifetime safety, recommend a rollover
or optimize a policy. Source zero-basis, eligibility, separation, RMD and IRA
age/basis boundaries remain those of ADR0051. Full-account factor proxies are
entered assumptions, not confirmed underlying security holdings. Terminal
marked wealth is not a complete after-tax liquidation value. Broader wrapper
profiles, household RMD corrections, retirement optimization and release
validation remain open tickets.
