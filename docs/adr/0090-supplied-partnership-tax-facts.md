# ADR 0090: Independently supplied partnership income, SE, QBI and AMT facts

Status: tax foundation for conditional drilling-partnership ticket #13. No new dependency. The existing Annual tax editor exposes every field and the existing dated tax-event ledger can carry the same numeric facts.

## Independent classifications

`allowed_nonpassive_partnership_income` is signed, already allowed ordinary partnership income/loss after applicable basis, at-risk, passive, excess-business-loss and other limitations. The pre-existing `allowed_passive_income` remains a distinct signed input. Neither field determines legal eligibility or creates a cash receipt. Federal/NJ income classifications remain independent.

Nonpassive ordinary income maps into total Schedule E income `e02000` and its non-section-1411 subset `e26270`. The installed Tax-Calculator 6.8.5 NIIT implementation subtracts that subset from Schedule E investment income. Thus a supplied nonpassive loss does not automatically offset unrelated investment income for NIIT. This remains a supplied non-section-1411 classification, rather than an inference from the words general partner, working interest or active.

`partnership_se_earnings_primary/spouse` independently supply the applicable K-1 box 14 earnings through `k1bx14p/s`. The existing calculator computes SE tax, the deductible part and wage-cap/additional-Medicare interactions. SE tax already enters its Form 1040 total and is not charged again as employee payroll. Results expose SE tax and the deductible amount separately. A positive nonpassive amount never automatically generates or excludes applicable SE earnings; the caller must supply the correct earnings facts. Spouse earnings require joint filing.

`partnership_qbi_before_se_deduction`, `partnership_qbi_w2_wages` and `partnership_qbi_qualified_property` independently supply already-eligible, already-history-adjusted non-SSTB QBI facts. QBI loss carry, aggregation, SSTB classification, REIT/PTP rules and other eligibility are not inferred. The calculator applies its deduction limits and subtracts its independently computed deductible SE tax. Zero supplied QBI explicitly produces no assumed QBI deduction.

Tax-Calculator otherwise derives QBI from the entire `e26270` amount. We use **`e27200` solely as a numerical QBI offset**, equal to supplied QBI before SE deduction minus supplied nonpassive income. No actual farm-rental input is supported. Every installed `calcfunctions.py` use was checked: `e27200` enters the QBI build, while NIIT and AGI retain the actual `e02000/e26270` amounts. This is not a claim that partnership income is farm rent. A future farm-rental adapter or package upgrade must revisit this deliberate carrier and its independent checks.

`additional_amt_income` supplies nonnegative income present for AMT but absent from regular AGI through the documented `cmbtp` input. It changes current AMT without inventing regular income. It does not calculate IDC preference eligibility, AMT basis or minimum-tax credit history. Those missing facts must be disclosed by a consumer; this primitive is not a complete business-return or full-tax optimization certificate.

## Existing scope guards

The old pre-FRA no-work bridge now includes supplied positive partnership SE earnings alongside wages, preserving its conservative rejection until the earnings-test adapter supports them. The existing combined IRA contribution workbench rejects partnership SE compensation until a dedicated compensation/MAGI adapter is supplied. These guards avoid silently treating new earned amounts as absent. Consumer-generated events must also validate these unsupported combinations before projection.

## Evidence and checks

Checked October 25, 2026: [Tax-Calculator input documentation](https://taxcalc.pslmodels.org/guide/input-vars/) describes `e02000`, `e26270`, `k1bx14p/s`, QBI wages/property and `cmbtp`. The pinned installed implementation supplies the exact numerical behavior above. [2025 IRS K-1 instructions](https://www.irs.gov/instructions/i1065sk1) separately report self-employment earnings and qualified-business-income information. [2025 Publication 925](https://www.irs.gov/publications/p925), also located/read through the existing local tax-reference collection, separates basis/at-risk limits from passive limits and describes the oil/gas working-interest exception with its liability conditions. These sources do not qualify a particular product. [2025 Form 6251 instructions](https://www.irs.gov/instructions/i6251) support the independent current-AMT check.

Checks compare passive/nonpassive gains and losses with identical AGI and independently expected NIIT; verify separately supplied QBI; reconcile $10,000 box-14 earnings to SE tax and its deduction; exercise the Social Security wage cap and additional Medicare; reconcile the 2025 single-filer AMT exemption/rate example; and verify cache isolation plus actual Annual tax form submission. No gross deduction times a headline rate is deposited as tax-saving cash.

For checkout-local review of this deliberate adapter, the pinned [6.8.5 `TaxInc` implementation](https://github.com/PSLmodels/Tax-Calculator/blob/6.8.5/taxcalc/calcfunctions.py#L1905-L1916) builds:

```python
qbinc = max(0., e00900 - c03260 - e03300 - e03270
            + e26270 + e02100 + e27200)
```

Its [NIIT implementation](https://github.com/PSLmodels/Tax-Calculator/blob/6.8.5/taxcalc/calcfunctions.py#L2864-L2867) uses `line4c = e02000 - e26270` when `NIIT_PT_taxed` is false. The integration oracles in `tests/test_partnership_tax_channels.py` and `tests/test_partnership_se_amt.py` exercise the real pinned calculator with equal-AGI passive/nonpassive inputs, zero/positive QBI and independent SE/AMT channels. These independently expected results, rather than a test mirroring package source, constrain this version-specific adapter.
