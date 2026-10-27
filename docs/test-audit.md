# Main-branch test audit — October 27, 2026

This pass applies the previously approved test audit to public main at `cf74e427ddb373c87b7ece8da8a9e1e6155bea68`. It is a main-only subset of the larger integrated-branch audit; it does not claim that pending feature tests were published or removed.

The rule in [AGENTS.md](../AGENTS.md) requires user buy-in before adding complexity for speculative or vanishingly unlikely race/security cases. The approved removals cover speculative internal-object checks, repeated schema/dispatch assertions and duplicate UI/serializer calculations. Independently expected taxes, cash/basis conservation, actual funding/settlement failures and meaningful user controls remain.

| Main snapshot | Before | After | Removed |
| --- | ---: | ---: | ---: |
| Collected pytest cases | 2,646 | 2,406 | 240 |
| Test function definitions | 1,779 | 1,598 | 181 |
| Test modules | 716 | 648 | 68 |

Applied 150 exact source-audit patches and two scrutinized partial patches: 152 existing test files changed, including 68 complete test-module deletions and one removed test helper (`tests/local_file_cases.py`). All 69 complete file deletions matched the audited files byte for byte. No production code, workflow, dependency, quality threshold or future-feature test was changed. No replacement tests were added.

The restored foreign-credit eligibility control and NJ wash-sale override remain in `tests/test_foreign_credit_ui.py` and `tests/test_lot_tax_ui.py`. Independent PR review also retained the existing `test_generated_price_form_requires_explicit_replacement_confirmation` in `tests/test_exchange_fund_ui.py`: it is the sole check that supplied observations are replaced by generated prices only after explicit confirmation. That complete file now matches the original main snapshot.

## Changed contexts retained deliberately

- `tests/test_policy_search_compile.py`: removed the identical audited IRA-plan check. Kept main’s unsupported-option exit-integration test and its import: the source audit removed a different later market-binding test.
- `tests/test_local_product_reports.py`: removed the audited forged/nonfinite-object matrix and its unused import. Kept five existing complex-product report/import cases because the larger audit retained different QOZ/complex-product cases not yet part of main’s version of this module. The audited file was not a complete-module deletion.

## Source-audit paths absent from this main tree

These 44 paths were not imported, restored or otherwise edited. Some paths were already pruned by owner-branch updates before those owners landed; others belong to unpublished features. They are excluded from the main-only counts above.

```text
tests/test_advisory_billing_guards.py
tests/test_advisory_funding_boundaries.py
tests/test_advisory_reservation.py
tests/test_advisory_snapshot_ui.py
tests/test_advisory_ui.py
tests/test_drilling_household_ui.py
tests/test_drilling_market_modes.py
tests/test_drilling_optimizer_envelope.py
tests/test_drilling_optimizer_native_validation.py
tests/test_drilling_optimizer_reference.py
tests/test_drilling_optimizer_selection.py
tests/test_drilling_optimizer_source_guards.py
tests/test_drilling_saving_ui.py
tests/test_exchange_allocation_ui.py
tests/test_foreign_tax_redetermination_ui.py
tests/test_local_optimizer_output.py
tests/test_local_optimizer_reports.py
tests/test_new_life_offer_selection.py
tests/test_optimizer_advisory_scope.py
tests/test_optimizer_advisory_ui.py
tests/test_partnership_tax_ui.py
tests/test_policy_collectible_ui.py
tests/test_policy_contract_boundaries.py
tests/test_policy_contract_guards.py
tests/test_policy_contract_ui.py
tests/test_policy_drilling_ui.py
tests/test_policy_exchange_ui.py
tests/test_policy_new_life_ui.py
tests/test_policy_option_allocation_guards.py
tests/test_policy_option_allocation_ui.py
tests/test_policy_qoz_ui.py
tests/test_pr_execution_gain_ui.py
tests/test_pr_prepared_engine_threads.py
tests/test_property_ui.py
tests/test_qoz_household_reporting.py
tests/test_qoz_market_compile.py
tests/test_qoz_market_guards.py
tests/test_qoz_market_modes.py
tests/test_qoz_market_ui.py
tests/test_qoz_optimizer_audit_guards.py
tests/test_qoz_optimizer_exits.py
tests/test_qoz_optimizer_unfunded.py
tests/test_qoz_ui.py
tests/test_release_advisory_replay.py
```

## Already applied on main

The following 11 existing files already matched the approved post-audit content and were left unchanged:

```text
tests/test_drilling_denied_basis.py
tests/test_drilling_life_combined.py
tests/test_drilling_market_scope.py
tests/test_drilling_options_combined.py
tests/test_drilling_terminal_pending.py
tests/test_foreign_credit_ui.py
tests/test_foreign_tax_ui.py
tests/test_local_offline.py
tests/test_nj_residence_ui.py
tests/test_spain_assessment_ui.py
tests/test_spain_ui.py
```

## Validation

Initial collections succeeded: 2,646 cases before and 2,405 after. Final review restores one existing case, yielding 2,406. The single full post-pruning run passed all **2,405 tests** with **93.75% branch-aware coverage** in **561.96 seconds**. Ruff lint, formatting, typing and the unchanged complexity/maintainability/size gates passed across **1,468 first-party Python files**. The 85% coverage requirement remains unchanged. Test and production files stayed frozen throughout that run; this report’s validation paragraph was completed afterward.

These are local results for this main-only code/test tree. Fresh public-head CI and independent review remain required before merge.

The existing exchange-price replacement confirmation check was restored after the full run; its focused UI verification and fresh CI validate the final head. The full-run coverage above belongs to the frozen 2,405-case checkpoint, not a claimed second full run.
