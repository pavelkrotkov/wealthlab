"""Explicit original synthetic eligibility/limit facts; no named sponsor terms."""


def limits(amount="1000000"):
    return dict(basis=amount, at_risk=amount, passive=amount, other=amount)


def timing(treatment="allowed"):
    return dict(
        treatment=treatment,
        release_on="2027-12-31" if treatment == "deferred" else None,
        eligibility_after_limits_assumed=treatment != "denied",
    )


def deduction(identity, component, amount, treatment="allowed"):
    return dict(
        id=identity,
        provenance="illustration",
        component=component,
        federal_requested=str(amount),
        nj_requested=str(amount),
        federal_limits=limits(),
        nj_limits=limits(),
        federal_timing=timing(treatment),
        nj_timing=timing(),
        federal_basis_reduction=str(amount),
        nj_basis_reduction=str(amount),
        at_risk_reduction=str(amount),
    )


def terms():
    return dict(
        account_id="drilling",
        legal_form="general_partner",
        federal_ordinary="nonpassive_assumption",
        working_interest_eligibility_supplied_confirmed=True,
        ordinary_nonsection1411_classification_supplied_confirmed=True,
        se_classification="supplied_box14",
        se_classification_basis="Synthetic box14 facts; classification supplied independently",
        supplied_qbi_amt_history_and_limits_confirmed=True,
        all_cash_basis_terms_and_recognition_complete_confirmed=True,
        paid_operating_costs_deductible_assumption_confirmed=True,
        other_tax_inputs_exclude_product_confirmed=True,
        household_recourse_for_modeled_creditors=True,
        unmodeled_liability_risk_acknowledged=True,
        opening_cash="0",
        opening_property_value="0",
        opening_federal_basis="0",
        opening_nj_basis="0",
        opening_at_risk="0",
        opening_reference_price="100",
        federal_recapture_limit="70000",
        nj_recapture_limit="70000",
        nj_exit_category="partnership",
        residual_capital_niit_inclusion_assumed_confirmed=True,
        residual_federal_capital_character="long_term",
        federal_exit_loss_limits=limits(),
        nj_exit_loss_limits=limits(),
        federal_exit_loss_timing=timing("denied"),
        nj_exit_loss_timing=timing("denied"),
        reference_nj_wash_treatment="no_wash_assumption",
        reference_zero_fees_and_no_external_identical_trades_confirmed=True,
    )
