"""Fixed home context uses one actual close while policy choices retain original capital.

Early retirement:540000 opening wealth-48000 spending-3600 interest-10000
closing costs-1 stock commission-770 actual NJ tax=477629. Retaining or
failing to close the home leaves240000 equity and60000 debt, never exit cash.
"""

import json
from pathlib import Path

from optimization_cases import flat
from streamlit.testing.v1 import AppTest

from wealthlab.household.funding import opening_wealth
from wealthlab.optimization.inputs import PolicySearch
from wealthlab.optimization.property_example import extend
from wealthlab.optimization.search import search


def test_fixed_home_optimizer_cash_and_retained_or_failed_close_limits():
    case = extend(flat())
    data = case.model_dump(mode="json")
    holding = data["household"]["property_plan"]["holdings"][0]
    holding["sale"].update(federal_taxable_gain="40000", nj_taxable_gain="50000")
    case = PolicySearch.model_validate(data)
    original = case.model_dump_json()
    result = submit(original)
    early, later = result["candidates"]
    rows = result["selected_training"]["details"][0]["rows"]
    close, final = rows[5], rows[-1]
    plan = case.household.property_plan
    assert plan is not None
    assert dict(
        opening=opening_wealth(case.household),
        early=(early["median_real_after_tax_exit_wealth"], early["median_net_cash_tax"]),
        later_identity=later["median_real_after_tax_exit_wealth"] + later["median_net_cash_tax"],
        selection=(result["configured_validation_passed"], result["selection"]),
        close=(close["property_cash_received"], close["property_debt_principal_paid"]),
        interest=(close["property_debt_interest_paid"], close["debt_payment"]),
        other_service=sum(r["debt_payment"] for r in rows),
        remaining=(final["account_balances"]["home"], final["debt_balances"]["home_lien"]),
        audit=final["property_audit"]["inputs"],
        unchanged=case.model_dump_json(),
    ) == dict(
        opening=540000,
        early=(477629, 770),
        later_identity=538399,
        selection=(True, "candidate_1"),
        close=(229400, 60000),
        interest=(600, 0),
        other_service=3000,
        remaining=(0, 0),
        audit=plan.model_dump(mode="json"),
        unchanged=original,
    )
    alternatives = []
    for action in ("retain", "blocked"):
        changed = json.loads(original)
        home = changed["household"]["property_plan"]["holdings"][0]
        if action == "retain":
            home.update(terminal_action="retain", sale=None)
        else:
            home["observations"][5]["locked"] = True
        other = search(PolicySearch.model_validate(changed))
        candidate = other["candidates"][0]
        alternatives.append(
            (
                other["selection"],
                candidate["median_marked_real_wealth"],
                candidate["median_ending_property_equity"],
                candidate["median_ending_property_debt"],
                candidate["median_real_after_tax_exit_wealth"],
                candidate["joint_success_fraction"],
            )
        )
    assert alternatives == [
        (None, 477599, 240000, 60000, None, 1),
        (None, 477599, 240000, 60000, None, 0),
    ]


def submit(original):
    page = AppTest.from_file(Path(__file__).parents[1] / "app.py", default_timeout=120).run()
    page.radio[0].set_value("Optimize").run()
    page.checkbox(key="property_context").check().run()
    shown = json.loads(page.text_area(key="policy_search_editor").value or "")
    assert shown["household"]["property_plan"] is not None
    page.text_area(key="policy_search_editor").set_value(original)
    page.button(key="FormSubmitter:policy_search-Search allowed policies").click().run()
    assert (len(page.exception), len(page.error)) == (0, 0)
    return page.session_state["policy_search_result"]
