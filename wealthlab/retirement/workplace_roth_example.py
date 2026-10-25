"""Original ordinary Roth plan cash:9400federal/9000conditionalNJ cost in10000value.

At55 after separation at54, a5000 nonqualified payment recovers4700/4500cost,
recognizes300/500income, withholds60federal and has30additionalfederalage tax.
"""

from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace_withdrawal_example import synthetic as workplace
from wealthlab.tax.projection_example import template as tax_template


def synthetic():
    data = workplace().model_dump(mode="json")
    data.update(name="Synthetic designated Roth plan cash and separate cost", hsa_plan=None)
    data["accounts"] = [
        dict(a, id="work_roth", wrapper="roth", balance=10000) if a["id"] == "work_pretax" else a
        for a in data["accounts"]
        if a["id"] != "cash_hsa"
    ]
    data["workplace_plan"].update(
        products=dict(work_roth="roth_401k"),
        cash_withdrawals=None,
        roth_cash_withdrawals=dict(
            contracts=dict(ordinary=contract()),
            orders=[
                dict(
                    id="roth_cash",
                    provenance="illustration",
                    date="2026-02-01",
                    source="work_roth",
                    amount=5000,
                )
            ],
            timing="first_day_before_employee_deferrals_and_month_end_returns",
            rule_mode="frozen_2026_ordinary_designated_roth_cash",
        ),
    )
    scenario = Scenario.model_validate(data)
    data["tax_plan"] = tax_template(scenario).model_dump(mode="json")
    return Scenario.model_validate(data)


def contract():
    return dict(
        sources=["work_roth"],
        separation_date="2025-12-01",
        first_federal_contribution_year=2016,
        federal_basis=9400,
        nj_basis=9000,
        complete_vested_ordinary_designated_roth_contract_confirmed=True,
        no_inplan_conversions_inherited_loans_nua_or_other_special_history_confirmed=True,
        complete_cash_events_excluded_from_other_inputs_confirmed=True,
        nj_treatment="conditional_same_qualification_and_pro_rata_cost",
        independent_nj_basis_and_conditional_treatment_confirmed=True,
    )
