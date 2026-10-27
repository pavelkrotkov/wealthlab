# Fixed native home and debt context in bounded policy search

Status: conditional optimizer integration for issue18. Reuses the actual personal-home book in [ADR0160](0160-source-property-and-native-lien-close.md); no property-sale or relocation dimension is introduced.

## Shared source facts and native execution

The existing optimizer accepts a fixed `property_plan` and requires native property accounts to have that plan. Every candidate keeps the same original home, linked household debts, dated observations, supplied tax bases/recognition, closing costs and declared retain/sell action. Retirement, sale/harvest, wrapper and other already supported controls continue through their existing compilation. Imported inputs never pass through a synthetic property factory.

The existing shared-market executor already preserves independently supplied home observations and executes the native property ledger. It pays actual mortgage principal/current-month interest through the original debt balances, posts separately supplied tax recognition with zero event cash and deposits net closing proceeds once. No new tax, cash, valuation or debt engine is added. Property values do not inherit an equity factor or invented historical home returns. Failed required closes retain native product/joint funding failures.

Terminal ranking additionally reads the native property economic-state audit: every linked home must actually close, have no blocked close and retain zero gross home value/linked debt. Zero net equity alone does not establish closure. A retained home remains marked wealth and illiquid equity, with its real debt and service still present; it receives no completed after-tax exit value. Candidate tables separately report median ending property equity and linked debt without subtracting either again from wealth.

## Editable original example

Optimize / Short composable examples offers **Add fixed synthetic home and native mortgage close**. The common original household adds a300000 home and60000 lien; its existing retirement choices all retain one June close and supplied property facts. Age100,95% success and two-year reserves remain the default targets. The short horizon does not establish retirement safety.

Native home issuer/factor coverage remains unmeasured, as before. The example explicitly disables the optional issuer limit and states that assumption beside the control. Imported households retain their own limit; no coverage is fabricated and no real source terms are regenerated. Existing JSON input/export permits a supplied retain or different fixed close, with no automatic property choice.

## Independent financial evidence

One real UI/optimizer regression uses flat prices, full stock basis and the explicitly reduced age50 test horizon. Original equity540000 minus48000 spending,3600 actual lien interest,10000 close costs,1 stock commission and770 actual NJ tax leaves477629 early-retirement cash. The later retirement adds60000 actual W2 cash, less its actual combined taxes. The native June close deposits229400, pays60000 principal/600 interest and leaves zero property/debt; generic debt service pays only the preceding3000. The source plan remains unchanged.

The same regression checks supplied retain and locked-close cases: both retain240000 illiquid home equity,60000 actual debt and477599 marked ending wealth for early retirement. Neither ranks as a completed exit. The retained case remains jointly funded; the locked required close fails joint feasibility. These are synthetic source assumptions, not inferred exemptions, deduction rights or home-price forecasts.

Coverage and current-head publication/review remain separate validation gates. Existing property cash, blocked-close, market, saving, fee, product-exit, employment and optimizer controls are reused; no per-helper or speculative schema test suite was added.

Validation:58 distinct affected financial/UI checks pass across the new end-to-end regression and existing native property, optimizer, product and contract controls. Combined statement/branch coverage is88.55% over the five selected affected modules, above the unchanged85% requirement. Global Ruff, formatting and typing pass; all1818 discovered first-party Python files satisfy CC≤8, MI≥50, SLOC≤300 and function span≤60. Current-head CI and independent review are still required before merge.
