"""Real linked-sale/cash/tax conservation; assertions use independently derived amounts."""

from decimal import Decimal

from qoz_cases import edited, flat

from wealthlab.household.projection import project
from wealthlab.products.qoz_compare import compare

D = Decimal


def test_source_proceeds_and_reinvestment_are_not_deposited_or_recognized_twice():
    rows = project(flat())
    first, final = rows[0], rows[-1]
    assert first["account_balances"] == dict(cash=D(25000), brokerage=D(0), qoz=D(80000))
    assert first["net_wealth"] == D(105000)  # $100k stock + $5k cash, all flows internal.
    assert final["qoz_settlement_cash"] == D(80000)
    assert final["account_balances"]["qoz"] == 0
    assert final["closing_cash"] + final["tax_position"] <= D(105000)


def test_source_gain_identity_and_character_survive_reinvestment():
    final = project(flat())[-1]
    call = final["qoz_audit"]["calls"][0]
    assert call["elected"] == dict(federal=D(80000), new_jersey=D(70000))
    assert final["lot_audit"]["disposals"][0]["proceeds"] == D(100000)
    tax = final["qoz_audit"]["tranches"][0]["tax"]
    includes = [r for r in tax["log"] if r["event"] == "deferred_gain_inclusion"]
    assert [r["amount"] for r in includes] == [D(80000), D(70000)]


def test_delayed_sale_cash_is_wealth_but_cannot_pay_a_tax_bill():
    scenario = edited(flat(), settlement_months=6, federal="denied", new_jersey="denied")
    data = scenario.model_dump(mode="json")
    data["accounts"][0]["balance"] = "0"
    data["qoz_plan"]["calls"][0]["amount"] = "100000"
    rows = project(type(scenario).model_validate(data))
    assert rows[-1]["qoz_receivable"] == D(100000)
    assert rows[-1]["closing_cash"] == 0
    assert rows[-1]["tax_unfunded"] > 0
    assert rows[-1]["funding_failure"]
    assert rows[-1]["net_wealth"] == D(100000) - rows[-1]["tax_position"]


def test_denied_deferral_and_allowed_preserve_the_same_underlying_economic_audit():
    result = compare(flat())
    audits = [result["rows"][name][-1]["qoz_audit"] for name in ("denied", "deferred", "allowed")]
    economic = [economic_only(r) for r in audits[0]["months"]]
    for audit in audits[1:]:
        assert economic == [economic_only(r) for r in audit["months"]]
    assert audits[0]["economic_log"] == audits[2]["economic_log"]
    assert all(a["terms"]["new_jersey"] == "allowed" for a in audits)
    assert result["rows"]["liquid_reference"][-2]["qoz_settlement_cash"] == D(80000)


def economic_only(row):
    return {key: value for key, value in row.items() if key != "original_gain_included"}
