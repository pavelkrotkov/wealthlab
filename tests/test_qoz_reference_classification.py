"""A liquid reference cannot combine its liquid economics with QOF-only tax elections."""

import pytest
from optimization_qoz_cases import case, changed
from qoz_cases import flat

from wealthlab.household.projection import project
from wealthlab.optimization.validation import validate


def test_native_reference_cannot_receive_qof_only_tax_treatment():
    household = flat()
    reference = household.qoz_plan.model_copy(update={"mode": "liquid_reference"})
    with pytest.raises(ValueError, match="cannot elect QOZ"):
        project(household.model_copy(update={"qoz_plan": reference}))


def test_reference_offer_cannot_choose_a_benefit_or_delay_its_liquid_settlement():
    with pytest.raises(ValueError, match="denied tax elections"):
        validate(changed(case(), lambda d: d["qoz_offers"][-1]["plan"].update(federal="allowed")))
    with pytest.raises(ValueError, match="immediate settlement"):
        validate(changed(case(), lambda d: d["qoz_offers"][-1]["plan"].update(settlement_months=1)))


def test_changed_source_lot_ids_cannot_create_a_new_gain_election_profile():
    with pytest.raises(ValueError, match="source lots"):
        validate(
            changed(
                case(),
                lambda d: d["qoz_offers"][2]["plan"]["calls"][0].update(source_lot_id="invented"),
            )
        )
