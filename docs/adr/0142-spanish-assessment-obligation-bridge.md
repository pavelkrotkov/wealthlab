# ADR 0142: Pure Spanish annual assessment and obligation bridge

Status: implemented above the regional Spain layer for issue #16 and the shared cash/credit integration in #17. No new dependency. `SpainAssessmentPlan` and `evaluate_plan` compose the existing annual engine rather than another tax or wallet implementation.

## Identity and source contract

A plan contains an explicit as-of date, independently classified person/year annual cases, stable annual assessment IDs and remaining scheduled tax obligations. It allows one current assessment per person/liability year; rerunning an updated case retains that assessment ID. Different people keep separate individual caps and ownership. Summing their nominal EUR assessments is not joint filing, a discounted comparison or household after-tax wealth.

Each annual case retains its source-income IDs, separately translated acquisition/proceeds, fiscal wealth/debt, region, recognition limitations and payment records. Source-income identity is scoped by person and liability year; an asset/source label can recur across years without duplicating a payment. Payment IDs are globally unique across the plan, preventing the same observed tax from being recognized in two annual cases. Annual source IDs and schedule IDs must be unique. A schedule identifies its annual assessment and tax type. Its explicit source supports the assumed due date and remaining amount; the adapter does not infer a statutory deadline.

Only completed annual fiscal snapshots are supported. A snapshot cannot include observations after the plan's as-of date, and plan/case synthetic provenance must agree. Later liability years still require the annual engine's explicit frozen-2025 policy. A later observation date does not change the liability year or automatically reclassify an income/product.

## Assessment and remaining schedules

Each annual result exposes assessed IRPF/IP/solidarity liability, observed recognized payments, outstanding amounts and informational overpayments. Observed payments are distinct from their actual cash values/FX and from unexecuted schedules. An informational overpayment is not a confirmed refund entitlement or a new cash receivable. The annual engine's explicit unsupported IP-overpayment adapter boundary remains intact.

`SpanishTaxObligation.amount_eur` means the **remaining** scheduled amount at the plan's as-of date. The executing book owns allocation of actual payments/refunds and must update remaining schedules on a later reconciliation. The pure adapter never allocates a receipt automatically. Multiple remaining installments for one assessment/tax type must collectively fit its assessed outstanding amount. If they exceed it, every affected installment is blocked; input order cannot select a favored fundable installment.

A blocked income classification blocks the dependent wealth assessment and related obligations. A wealth-only block retains independently resolved IRPF and its eligible remaining schedules. Blocked obligations have `fundable_eur=None`; they must not enter cash execution. A schedule never enters `case.payments`, so scheduling a full IP bill does not create solidarity's actually-paid IP credit. Newly observed actual IP payment can change solidarity and outstanding IP on a rerun; obsolete remaining schedules are then blocked until updated.

## One actual cash book

Issue #17 owns the single foreign-tax cash/refund/funding book, actual payment allocation, USD/native-currency execution, owed/refund positions, credit observation years and US foreign-tax-credit revisions. This Spain adapter emits stable assessment/obligation identities, conditional/blocked assessment snapshots and unexecuted EUR schedules. It does not debit cash, sell assets, infer a funding gain's Spanish classification or create bilateral relief. `cash_execution_supported` and `full_bilateral_optimization_supported` remain false.

The actual executing consumer must retain owner, liability year, tax type, settlement date, actual native-currency FX and original recognized-tax reversal. Currency translation of a EUR assessment into a later USD funding requirement belongs to that dated execution, not an annual scalar. Required foreign-tax funding must precede optional subscriptions and optional saving, preserving the existing household conservation and funding solver.

## User workflow and evidence

Products / Spain annual tax schedules offers an editable/importable three-case synthetic plan: one person's two years and another person's independently supplied region. It evaluates actual annual engine results, reconciles remaining schedules, renders blocked reasons and exports the complete inputs/results. Invalid edits clear stale results. No private household facts, identity or eligibility are inferred.

Checks independently assert the combined sum from the previously verified annual oracles, separate people/year assessments, immutable/repeatable evaluation, no credit from scheduled IP, actual-IP observation updates, collective over-allocation blocks and informational-only IRPF overpayment. Refund checks retain the original tax reversal (EUR40) separately from actual refund cash (USD50 at EUR1.1), leaving EUR60 recognized IP paid rather than deriving a credit from the new cash FX. Identity/chronology checks reject duplicate person/year assessments, cross-person duplicate payment IDs, missing assessment references and future observations. Real Streamlit tests exercise submit/export, blocked schedules, invalid-result clearing and the Products route.

Primary tax scope remains ADR0140/0141 and their verified official sources. This layer adds no domestic classification, residence entitlement, treaty-credit formula or legal deadline. Its original synthetic schedules are explicit assumptions.
