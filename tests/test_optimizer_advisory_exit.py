"""Cash-only marks cannot establish closure while an actual advisory bill remains owed."""

from copy import deepcopy
from decimal import Decimal

from tests.optimizer_advisory_cases import case, selection
from wealthlab.markets.household_run import run
from wealthlab.markets.paths import generate
from wealthlab.optimization.assessment import completed_exit
from wealthlab.optimization.compile import compile_candidate


def executed():
    model = case()
    household, binding = compile_candidate(model, selection(model, 0, False))
    rows = run(household, generate(model.training), binding)["details"][0]["rows"]
    return household, rows


def test_unpaid_fee_and_missing_native_fee_audit_prevent_completed_exit():
    household, rows = executed()
    assert completed_exit(household, rows) is True
    unpaid = deepcopy(rows)
    unpaid[-1]["fees_owed"] = unpaid[-1]["advisory_fees_owed"] = Decimal(10)
    assert completed_exit(household, unpaid) is False
    missing = deepcopy(rows)
    missing[-1].pop("advisory_fee_audit")
    assert completed_exit(household, missing) is False


def test_zero_liability_from_a_different_fee_contract_is_not_actual_common_execution():
    household, rows = executed()
    changed = deepcopy(rows)
    changed[-1]["advisory_fee_audit"]["inputs"]["schedules"][0]["fixed_per_period"] = "0.01"
    assert completed_exit(household, changed) is False
