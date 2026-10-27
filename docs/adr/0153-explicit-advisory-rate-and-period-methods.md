# Explicit advisory rate and annual-period interpretations

Status: unpublished native contract extension. Existing wallet, fee arrears, snapshot, source availability and month-end billing conventions are unchanged.

## Rate interpretation is a supplied fact

`AdvisorySchedule.rate_application` defaults to `progressive_marginal`: each rate applies only to its own eligible AUM band. The explicit alternative `whole_relationship_breakpoint` selects the first supplied band whose inclusive `upper_limit` contains the total actual covered eligible base, and applies that band's annual rate to the entire base. The final band remains unlimited; all finite limits must increase. This is one schedule's declared coverage, not an inference that every household account is managed or covered.

The whole-base alternative additionally requires `whole_relationship_breakpoints_source_confirmed=true`. The existing resolved schedule provenance, source reference, source date, availability date and confirmation of complete terms/value bases remain mandatory. A heading or unexplained table does not establish which method applies. Neither method is attributed to a real provider by this feature.

The audit reports `rate_application`, the original `marginal_tiers` for marginal billing, or one `whole_relationship_tier` containing the selected range, inclusive upper-limit convention, full actual base and applied rate. Marginal bands are not populated with whole-base charges. Unknown future AUM, gross borrowed assets and supplied valuation forecasts remain unsupported.

## Fixed annual factor is distinct from calendar time

A period can explicitly supply `fixed_annual_period_fraction` in `(0,1]`, paired with `fixed_fraction_source_confirmed=true`. Without both, the original calculation remains annual variable charge multiplied by actual exclusive accrual days divided by the declared annual `day_count`, preserving multiplication/division and currency-rounding order. A fully fixed-fraction schedule may omit an unknown unused `day_count`; any actual-day period requires an explicit supported annual day count. A supplied fraction instead multiplies the annual variable charge directly, with the same single rounding and the separately supplied fixed charge added once.

The existing schedule source must establish the fraction as well as the chosen rate interpretation. No quarter, month, holiday, partial engagement or termination automatically creates a fraction, proration or refund. Actual accrual start/end, valuation cutoff/date, assessment and payment-due date retain their meanings and existing validation. Advance billing still needs its separate sourced nonrefundable/no-proration confirmation. No first-day payment or future snapshot is fabricated.

The audit retains actual `period_days` and the entered `day_count`, while `period_factor_basis` explicitly distinguishes `actual_days_over_day_count` from `supplied_fixed_annual_fraction`. `fixed_annual_period_fraction` is null for actual-day billing; `applied_day_count` is null when the supplied fraction is used. A supplied fixed factor larger than one annual unit is outside this bounded alternative; existing actual-day periods retain their supported calendar behavior.

## Independent original checks and UI

Synthetic rates of 1.2% through $10,000 and .4% above it charge $43 versus $23 on the same $23,000 eligible base at a supplied quarter fraction. Exactly $10,000 remains in the inclusive first whole-base band; $10,000.01 selects the second rate on all eligible assets. A native shared-price shock moves observed AUM from $100,000 to $120,000 across a separately supplied $110,000 breakpoint; actual fees change without trading or rewriting shares/basis.

Fixed quarter fractions retain their $23 bill across 90/91/92-day service spans, leap years and entered 360/365/366 annual day counts. Absent fraction fields retain actual-day results. Partial cash pays only what exists, leaving one actual fee liability in net wealth; no loan, new account, capital or tax deduction is introduced. Fixed charges remain separate from the annual fraction.

Household's actual selected JSON import and fee editor expose these explicit fields and source flags. Imported whole-base/fixed-quarter input executes, then an edited marginal interpretation executes against unchanged capital and dates. The existing editable optimizer/source-envelope rules still apply: new normalized contract fields participate in input identity; the model does not silently reconfirm a stale source envelope or archived input fingerprint.

All new examples are original synthetic contracts and make no claim about any provider's rates, billing method or calendar terms. Public parents remain frozen until their independent integration/review gates.

Validation passed 141 combined native fee/optimizer/release/reservation checks with 91.99% affected branch coverage. A final 53-check targeted set, including confirmed advance fixed-fraction timing, passed with 96.19% across five implementation modules. The new billing helper has 95% branch coverage; unchanged 85% gates remain enabled. Ruff lint/format, type checks and all 1,579 first-party strict module/function gates pass. No wallet/reservation/snapshot implementation changed.
