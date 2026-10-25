"""Independent cash-only fund fixtures over the existing economic household example."""

from household_sleeve_cases import change, flat


def fund(cash=10000, **updates):
    def configure(data):
        sleeve = data["sleeve_plan"]["sleeves"][0]
        sleeve["case"].update(margin_policy="liquidate_on_breach")
        contract = dict(
            id="fund_contract",
            provenance="illustration",
            source_description="Synthetic no-provider contract and independent basis assumptions",
            eligibility_assumed_confirmed=True,
            limited_liability_no_calls_assumed_confirmed=True,
            cash_only_no_hot_assets_no_liability_changes_assumed_confirmed=True,
            tax_basis_schedule_complete_assumed_confirmed=True,
            lock_until="2026-01-01",
            dealing="monthly",
            notice_days=0,
            gate_fraction="1",
            settlement_days=0,
            federal_opening_basis="100000",
            new_jersey_opening_basis="100000",
            federal_capital_character="long_term",
            federal_exit_loss=dict(eligibility_after_limits_assumed=True),
            new_jersey_exit_loss=dict(eligibility_after_limits_assumed=True),
            requests=[],
            basis_adjustments=[],
        )
        contract.update(updates)
        sleeve["private_fund_contract"] = contract

    return change(flat(cash), configure)


def request(amount=0, notice="2026-01-01", final=False, identity="request"):
    return dict(
        id=identity,
        provenance="illustration",
        notice_date=notice,
        amount=str(amount),
        complete_liquidation=final,
    )
