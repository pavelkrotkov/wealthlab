"""Source-supplied dollar profiles cannot alter opening capital, legal terms or unit prices."""

VARIABLE = {
    "observations",
    "mode",
    "federal_recapture_limit",
    "nj_recapture_limit",
    "federal_exit_loss_limits",
    "nj_exit_loss_limits",
    "federal_exit_loss_timing",
    "nj_exit_loss_timing",
}
UNIT_FIELDS = (
    "date",
    "commodity_price",
    "royalty_fraction",
    "reference_price",
    "reference_locked",
    "exit_requested",
)
OPENING = (
    "opening_cash",
    "opening_property_value",
    "opening_federal_basis",
    "opening_nj_basis",
    "opening_at_risk",
    "opening_federal_tangible_basis",
    "opening_nj_tangible_basis",
)


def validate_decline(baseline, offer):
    if not offer.declined_no_prior_interest_or_obligations_confirmed:
        raise ValueError(
            "Confirm no prior drilling interest, obligations or new entry when declined."
        )
    if any(getattr(baseline, name) != 0 for name in OPENING):
        raise ValueError(
            "No-entry cannot erase existing drilling cash, property, basis or at-risk."
        )


def validate_fixed(baseline, proposed):
    if proposed.model_dump(exclude=VARIABLE) != baseline.model_dump(exclude=VARIABLE):
        raise ValueError(
            "Preserve original drilling account, opening capital and legal/rate terms."
        )
    left = [tuple(getattr(row, key) for key in UNIT_FIELDS) for row in baseline.observations]
    right = [tuple(getattr(row, key) for key in UNIT_FIELDS) for row in proposed.observations]
    if left != right:
        raise ValueError("Preserve drilling calendar, per-unit prices/royalties and dealing terms.")


def validate_mode_change(baseline, offer):
    if baseline.mode == offer.plan.mode:
        return
    if not offer.mode_change_no_prior_interest_or_obligations_confirmed or any(
        getattr(baseline, name) != 0 for name in OPENING
    ):
        raise ValueError(
            "Mode changes require zero prior components and independently confirmed no prior "
            "interest/obligations; an existing well needs an actual taxable transfer."
        )
