# Software reuse assessment

Current implementation uses the pinned packages and numerical comparisons documented in [executed reuse results](reuse-results.md) and [dependency notices](dependency-notices.md). The October 23 assessment below records the pre-spike research and is preserved as that dated decision history.

Research checked October 23, 2026. Repository documentation is evidence of intended capabilities, not proof of numerical correctness. No candidate has yet passed an executable integration spike.

| Candidate | Reuse decision | Relevant limits / next check |
|---|---|---|
| [OWL Planner](https://github.com/mdlacasse/Owl) | Test as a retirement optimizer and independent benchmark; prefer its existing solver to reimplementing retirement optimization where the inputs are representable. | Its [capability reference](https://github.com/mdlacasse/Owl/blob/main/info/modeling-capabilities.md) documents average-cost taxable accounting, long-term-only gains and no TLH. Standard deduction only and simplified state/move treatment also limit household use. It cannot be the authoritative lot/TLH ledger. Source is GPLv3; documentation is separately CC-BY-NC-SA and branding is reserved. Do not copy its docs or assets. |
| [Tax-Calculator](https://taxcalc.pslmodels.org/) | First federal-tax integration spike. Supports custom filing units, parameter reforms and marginal tax estimates; CC0 [license](https://github.com/PSLmodels/Tax-Calculator/blob/master/LICENSE). | Federal income and payroll model, not NJ, territorial or Spanish tax. Test capital characters, NIIT, itemization and wage inputs against independent examples. Verify policy horizon; extrapolated years must identify assumed law. |
| [PolicyEngine US](https://github.com/PolicyEngine/policyengine-us) | Evaluate NJ support and independent annual-tax cross-check before writing NJ rules. | Broad federal/state coverage does not establish correct partnership-category/basis treatment for this project. Inspect implementation and fixtures. [AGPLv3 license](https://github.com/PolicyEngine/policyengine-us/blob/main/LICENSE) affects distribution if integrated; decide licensing before adopting code. |
| [QuantLib](https://www.quantlib.org/) | Reuse option pricing and valuation infrastructure when required; [Python bindings](https://www.quantlib.org/download.shtml) and [BSD license](https://www.quantlib.org/license.shtml). | A pricing library does not supply household tax treatment, broker margin, assignment policy, historical quotes or a manager strategy. Test discrete dividends and American exercise assumptions separately. |
| [OpenTaxSolver](https://opentaxsolver.sourceforge.net/) | Candidate independent prior-year form-level check, not the forward projection core. | Current advertised tax-year package is 2025. Multi-year policy, path simulation and full instrument accounting need separate handling. Verify NJ and supported forms before relying on it. |
| [ProjectionLab](https://projectionlab.com/) | Product/UX comparison and optional manual cross-check. | Its [March 2025 announcement](https://projectionlab.com/blog/update-on-self-hosting) ended self-hosted feature updates and specified bug-fix support through December 2025. Not a maintained reusable local engine for this project. |
| [Boldin](https://help.boldin.com/en/articles/10377121-learn-more-about-boldin-s-unique-features) | Product comparison for spending, retirement and tax displays. | Its [tax-method explanation](https://help.boldin.com/en/articles/8482297-planner-operations-taxes) describes proprietary directional estimates. No reusable engine established. |
| [OpenRenta](https://www.openrenta.es/) and [Spanish tax calculators](https://github.com/luxeon/spanish-tax-calculators) | Discovery candidates for Spain; no adoption yet. | Need license review and tests of investment income, autonomous-community rules, wealth/solidarity taxes and cross-border treatment. Wage or self-employment calculators alone are insufficient. |
| Existing local research engine | Reuse verified algorithms and regression cases after separating configuration and data paths. | Existing code is tied to historical files, fixed tax-rate assumptions and conditional option accounting. Do not copy private fixtures, vendor datasets or whole scripts into the public repo. Extraction requires tests and provenance. |

## Proposed implementation direction

A small Python calculation package and Streamlit UI avoids separate frontend/API infrastructure. Use NumPy/SciPy for path generation and bounded policy search, a maintained tax package where it passes contract tests, and QuantLib for pricing. Lock dependencies after runnable spikes on local macOS and Linux. Benchmark OWL with synthetic cases that fit its documented domain; evaluate proposals with the same household ledger used for manual scenarios.

Do not combine independent calculators by adding their total taxes. Aggregate each jurisdiction's annual taxable events once, calculate liability once, and reconcile it to cash payments. Reuse must reduce custom code without silently dropping stock-lot, compensation or jurisdiction semantics.

## Cross-border authority starting points

The [IRS territorial guide, Publication 570](https://www.irs.gov/publications/p570) distinguishes bona fide residency and income source and has special rules for property owned before a move. Puerto Rico is not a zero-rate state switch. Local incentive eligibility and effective terms require current Puerto Rico authorities.

[AEAT residency guidance](https://sede.agenciatributaria.gob.es/Sede/en_gb/no-residentes/residencia-personas-fisicas-juridicas/persona-fisica-residente-espana.html) and [wealth-tax guidance](https://sede.agenciatributaria.gob.es/Sede/en_gb/Ayuda/23Presentacion/714_3_1.html) establish areas requiring specific rules. Spain must include regional rules, currency translation and applicable US interactions. These discovery references do not establish personal eligibility or certify a complete tax engine.

The NJ [February 2026 partnership bulletin](https://www.nj.gov/treasury/taxation/pdf/pubs/tgi-ee/git9p.pdf), pp. 2–5, and [2025 NJ-1040 instructions](https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf), printed pp. 11–12, require separate income-category treatment. A federal net loss cannot simply be multiplied by a combined federal/state rate. The local reference index was also consulted; its older snapshots are not current-law proof.

## October 24 — market-path implementation reuse

The path workbench reuses the installed pinned NumPy dependency for validated joint normal sampling and numerical summaries. No finance package or new dependency is needed for these explicitly assumed lognormal factors. Historical input, return conventions, provenance and stress overlays remain application responsibilities; neither a Gaussian sampler nor a factor chart establishes household funding success. See [the model and executed checks](adr/0024-paired-market-paths.md).

## October 25 — whole-life illustration reuse

[lifeLib's whole-life reference model](https://lifelib.io/libraries/uslib/products/whole_life/product-spec.html)
was reviewed for cash value, dividends, loan and nonforfeiture mechanics. Its
representative contract cannot supply missing terms for an actual policy.
Use supplied guaranteed/current/stressed schedules, with missing values explicit.
The already pinned QuantLib supplies dated NPV and Brent solving for money-weighted
returns; no new dependency is required. See [the implemented audit and numerical
checks](adr/0100-supplied-whole-life-illustrations.md). Contract tax, actual household
funding and a separately priced protection comparison remain follow-on work.
