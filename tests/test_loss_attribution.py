"""Current-loss sources reconcile, while actual tax benefit remains a matched comparison."""

import pytest
from test_lot_tax_reporting import forecast, reporting_case

from wealthlab.portfolio.cases import LotCase
from wealthlab.portfolio.engine import run
from wealthlab.portfolio.loss_attribution import USES


def loss_case():
    payload = reporting_case()
    payload["trades"] = payload["trades"][:1]
    payload["lots"][0].update(federal_basis="10750", nj_basis="10750")
    return payload


def first_year(payload):
    rows = run(LotCase.model_validate(payload))["annual_tax_comparison"]
    for row in rows:
        for allocation in row["federal_loss_use"].values():
            assert sum(allocation[key] for key in USES) == allocation["recognized_loss"]
    return rows[0]


def test_own_and_external_gains_ordinary_use_and_carry_reconcile():
    # Specific identification makes the intended 10,000 loss and 4,000 gain
    # independent of FIFO's ID tie break. The external short gain absorbs 2,000;
    # ordinary income consumes 3,000 and the final 1,000 remains available.
    payload = loss_case()
    gain = dict(payload["lots"][0], id="gain", federal_basis="0", nj_basis="0")
    payload["lots"].append(gain)
    payload["trades"].append(dict(payload["trades"][0], id="gain_sale", price="40"))
    payload["trades"][0].update(selection="specific", lot_ids=["original"])
    payload["trades"][1].update(selection="specific", lot_ids=["gain"])
    payload["lot_tax_cases"][0]["federal_income"]["short_term"] = "2000"
    row = first_year(payload)
    use = row["federal_loss_use"]["long_term"]
    assert use["recognized_loss"] == 10000
    assert use["own_gain_offset"] == 4000
    assert use["external_gain_offset"] == 2000
    assert use["ordinary_consumed"] == 3000
    assert use["ending_carry"] == 1000


def test_allocation_can_displace_opening_carry_without_incremental_tax_saving():
    # Both paths already offset all 5,000 gains and deduct 3,000 from wages.
    # The new loss only increases ending carry: showing the allocated 5,000
    # as a fresh tax saving would falsely credit an already sheltered gain.
    payload = loss_case()
    income = payload["lot_tax_cases"][0]["federal_income"]
    income.update(long_carry="20000", long_term="5000")
    row = first_year(payload)
    use = row["federal_loss_use"]["long_term"]
    assert use["external_gain_offset"] == 5000
    assert use["ordinary_consumed"] == 3000
    assert use["ending_carry"] == 2000
    assert use["opening_carry"] == 20000
    assert row["with_lot_trades"]["federal"]["long_carry"] == 22000
    assert row["incremental_liability"] == 0


def test_short_term_losses_net_first_and_consume_ordinary_allowance_first():
    # Long losses first offset the 2,000 long gain within their own character.
    # The external short loss still has first claim on the ordinary allowance;
    # a global "current losses first" rule would misattribute that deduction.
    payload = loss_case()
    payload["lot_tax_cases"][0]["federal_income"].update(short_term="-5000", long_term="2000")
    row = first_year(payload)
    use = row["federal_loss_use"]["long_term"]
    assert use["external_gain_offset"] == 2000
    assert use["ordinary_consumed"] == 0
    assert use["ending_carry"] == 8000
    assert row["with_lot_trades"]["federal"]["short_carry"] == 2000


def test_low_income_keeps_unused_deduction_in_carry():
    # With no positive taxable income before the loss, the carry worksheet
    # retains the entire loss despite the nominal 3,000 deduction on Schedule D.
    payload = loss_case()
    payload["lot_tax_cases"][0]["federal_income"]["wages_primary"] = "0"
    use = first_year(payload)["federal_loss_use"]["long_term"]
    assert use["ordinary_consumed"] == 0
    assert use["ending_carry"] == 10000


@pytest.mark.parametrize("change", ["pending", "retirement", "washed"])
def test_unrecognized_losses_are_not_allocated(change):
    # Economic losses are insufficient: an open wash window, IRA sale or
    # fully matched taxable replacement leaves no current recognized loss.
    payload = reporting_case()
    if change == "pending":
        payload.update(end="2026-06-15", trades=payload["trades"][:1])
    if change == "retirement":
        payload["accounts"][0]["wrapper"] = "roth_ira"
    use = first_year(payload)["federal_loss_use"]["long_term"]
    assert use["recognized_loss"] == 0


def test_next_year_opening_carry_is_not_claimed_as_a_new_loss():
    # This report traces current-year origins only. A later tax saving from
    # carry must stay in the annual comparison, not be relabeled a new harvest.
    payload = loss_case()
    payload["end"] = "2027-12-31"
    later = forecast(2027)
    later["federal_income"]["long_term"] = "5000"
    payload["lot_tax_cases"].append(later)
    first_year(payload)
    later = run(LotCase.model_validate(payload))["annual_tax_comparison"][1]
    use = later["federal_loss_use"]["long_term"]
    assert use["opening_carry"] == 7000
    assert use["recognized_loss"] == 0
    assert use["external_gain_offset"] == 0
    assert later["incremental_liability"] < 0


def test_capital_gain_distribution_uses_loss_as_own_gain_not_external():
    # Distribution income is part of modeled portfolio gains even though no
    # sale created it. Tax recognition, not payment, chooses the annual bucket.
    payload = loss_case()
    payload["price_only_marks_confirmed"] = True
    payload["distributions"] = [
        dict(
            id="capital",
            provenance="assumption",
            security_id="STOCK",
            ex_date="2026-05-01",
            payment_date="2026-05-02",
            recognition_date="2026-05-02",
            per_share="20",
            federal_character="long_term",
            nj_character="dispositions",
        )
    ]
    use = first_year(payload)["federal_loss_use"]["long_term"]
    assert use["own_gain_offset"] == 2000
    assert use["external_gain_offset"] == 0
    assert use["ordinary_consumed"] == 3000
    assert use["ending_carry"] == 5000
