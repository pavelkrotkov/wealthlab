"""Source scope is explicit and time bounded; a matching hash is not legal certification."""

from copy import deepcopy

import pytest
from optimization_drilling_cases import inputs

from wealthlab.optimization.drilling_scope import fingerprint, validate_envelope


@pytest.mark.parametrize(
    "field",
    [
        "all_candidate_employment_income_funding_and_bound_price_paths_confirmed",
        "supplied_legal_se_qbi_amt_history_limits_recapture_release_facts_confirmed",
    ],
)
def test_unconfirmed_legal_or_candidate_price_envelope_blocks_even_matching_inputs(field):
    household, _, confirmed, scope = inputs()
    unknown = confirmed.model_copy(update={field: False})
    with pytest.raises(ValueError, match="ALL candidates"):
        validate_envelope(household, unknown, scope)


def test_changed_search_inputs_cannot_reuse_a_previously_matching_source_envelope():
    household, _, confirmed, scope = inputs()
    changed = deepcopy(scope)
    changed["validation"]["seed"] += 1
    with pytest.raises(ValueError, match="Changed drilling search"):
        validate_envelope(household, confirmed, changed)
    assert fingerprint(scope) == fingerprint(dict(reversed(list(scope.items()))))


@pytest.mark.parametrize("field,value", [("as_of", "2026-01-02"), ("valid_through", "2026-01-31")])
def test_source_must_be_known_at_opening_and_cover_the_declared_full_horizon(field, value):
    from datetime import date

    household, _, confirmed, scope = inputs()
    altered = confirmed.model_copy(update={field: date.fromisoformat(value)})
    with pytest.raises(ValueError, match="known at opening"):
        validate_envelope(household, altered, scope)
