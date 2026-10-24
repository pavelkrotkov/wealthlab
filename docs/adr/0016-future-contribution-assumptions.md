# ADR 0016: Explicit forward contribution assumptions

Status: a retirement-ticket layer preparing forward wrapper funding. Does not complete contribution integration into the household tax wallet.

The standalone IRA/employee-401(k) and cash-HSA cases now accept future calendar years only with an explicit `rule_mode: "freeze_2026_assumption"`. The default `published` mode remains limited to this workbench's implemented 2025/2026 tables and rejects other years. The frozen mode is rejected before 2026. It is a conditional scenario, not a claim about future legislation or an assertion that later published limits do not exist.

The calendar year continues to determine age, event validity, contribution eligibility months, HSA establishment and age-based additional taxes. The rule base determines dollar limits, IRA phaseout bands and the implemented high-earner catch-up wage threshold. Freezing 2026 therefore retains the $150,000 prior-employer-wage threshold and required Roth treatment of covered high-earner catch-up contributions. It does not accidentally restore pretax catch-up merely because the calendar year has advanced. IRA compensation budgets, full-year MAGI and workplace coverage remain explicit caller inputs; neither future earnings nor legal eligibility is inferred.

For example, a conditional 2050 employee aged 60 receives the frozen $24,500 base deferral plus $11,250 special catch-up; supplied prior-employer wages above the frozen threshold route the catch-up into Roth. At age 64 the normal frozen catch-up is $8,000. An HSA owner born in 1995 with twelve supplied eligible self-coverage months has frozen capacity of $4,400 in 2049 and $5,400 in 2050 after reaching 55. These numbers are illustrations under frozen 2026 rules, not published 2049/2050 limits.

Both JSON editors retain the mode through input/result exports. Results display the rule base and mode next to the allocation. Existing published-year calculations are unchanged. Tests cover actual-year catch-up ages, future high-earner Roth treatment, HSA capacity and funded deductions, rejection of implicit future rules and backwards freezing, and both runnable UIs.

Published table sources and other unsupported eligibility/product rules remain documented in [contribution coverage](0005-retirement.md) and [HSA coverage](0007-hsa.md). A later published-rule update must add and validate its own dated tables; changing this assumption's label is insufficient.
