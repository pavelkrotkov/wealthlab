# 0101: Issuer concentration uses consistent marked-value precision

Observed household stress runs exposed a concentration slightly above 100% for a
single unlevered stock account after cash was spent. The numerator used actual
share quantities times unrounded market prices, while the gross-asset denominator
summed account balances rounded to cents. This could also report zero weight for
a positive but sub-cent position whose rounded account balance was zero.

Keep the actual cash, tax, account balances and net-wealth ledger unchanged.
For exposure only, add each known account's raw-mark minus cent-mark residual to
the reported gross-asset denominator. The shared account valuation helper serves
both taxable lots and invested HSAs. HSA distribution receivables and other
account cash already belong in the base denominator and are not counted again.
The audit exposes `market_gross_assets`; it does not clamp calculated weights or
turn unknown issuers into measured exposure. Noncash accounts without issuer
inventories remain explicitly incomplete.

Two actual household crash/lock regressions reproduced the original over 100%
result and now reconcile every observed single-issuer weight to stock/(stock+cash).
Independent cases check upward/downward cent rounding, a sub-cent raw position,
two accounts owning the same issuer, unchanged wallet cash and the invested-HSA
precision bridge. Existing actual HSA medical funding and market cash/tax/lock
checks remain part of validation. This correction completes a reporting edge
found during issue #8 acceptance runs; it does not change a policy decision or
improve any simulated funding result.
