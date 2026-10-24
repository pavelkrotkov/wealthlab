"""Distribution classification, state fractions and duplicate-tax context must be explicit."""

import pytest
from hsa_distribution_cases import change, flat

from wealthlab.household.projection import project


@pytest.mark.parametrize(
    "field,value,match",
    [
        ("nonqualified_treatment", "unconfirmed", "explicit tax assumption"),
        ("nj_withdrawal_taxable_fractions", {}, "independent NJ taxable fraction"),
        ("nj_withdrawal_taxable_fractions", {"missing": "0"}, "known withdrawal IDs"),
        (
            "generated_distribution_tax_excluded_from_other_inputs_confirmed",
            False,
            "excluded from other",
        ),
    ],
)
def test_incomplete_nonqualified_tax_assumptions_block_execution(field, value, match):
    def configure(data):
        data["hsa_plan"][field] = value

    with pytest.raises(ValueError, match=match):
        project(change(flat(), configure))
