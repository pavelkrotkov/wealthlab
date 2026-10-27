"""Native ordering and declared future creation remain binding after a closure assertion."""

from wealthlab.employment.compensation_exit_state import from_rows
from wealthlab.employment.compensation_termination_example import terminated
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario


def test_retained_cash_election_does_not_become_termination_settlement():
    # Retaining a requested payout keeps the existing vested dollars in the
    # employer account; a later closure assertion cannot settle those dollars.
    rows = project(terminated("retain"))
    result = from_rows(rows)["award"]
    assert rows[-1]["closing_cash"] == 74980
    assert result["account_balance"] == 20000
    assert result["cash_distributed"] == 0
    assert result["contractual_exit_proven"] is False


def test_earlier_termination_is_not_retroactively_validated_by_later_same_day_cash():
    case = terminated()
    # Sequence is contractual execution order, not merely a sorting display.
    # An earlier declaration must be rejected even if later trades exhaust value.
    order = {"termination": 0, "redeem": 1, "forfeit": 2, "exit_tax": 3}
    events = [
        event.model_copy(update={"sequence": order[event.id]})
        for event in case.compensation_plan.events
    ]
    plan = case.compensation_plan.model_copy(update={"events": events})
    rows = project(case.model_copy(update={"compensation_plan": plan}))
    result = from_rows(rows)["award"]
    assert result["dollar_positions_zero"]
    assert result["actual_balances_at_termination"] == dict(vested=20000, unvested=80000)
    assert result["contractual_exit_proven"] is False


def test_future_document_is_not_available_before_its_source_date():
    case = terminated()
    events = [
        event.model_copy(update={"source_date": case.end}) if event.kind == "termination" else event
        for event in case.compensation_plan.events
    ]
    plan = case.compensation_plan.model_copy(update={"events": events})
    result = from_rows(project(case.model_copy(update={"compensation_plan": plan})))["award"]
    assert result["contractual_exit_proven"] is None
    assert "cutoff" in " ".join(result["termination_reasons"])


def test_later_grant_then_forfeit_cannot_hide_post_termination_contractual_rights():
    # A later award is a remaining right even if forfeiture hides its final mark.
    # Testing both events prevents a terminal-balance-only shortcut.
    data = terminated().model_dump(mode="json")
    base = dict(tranche="award", provenance="illustration", sequence=0)
    data["compensation_plan"]["events"] += [
        dict(base, id="later_grant", kind="grant", date="2026-06-01", amount="1000"),
        dict(base, id="later_forfeit", kind="forfeit", date="2026-06-02", amount=None),
    ]
    rows = project(Scenario.model_validate(data))
    result = from_rows(rows)["award"]
    assert result["dollar_positions_zero"]
    assert result["contractual_exit_proven"] is False
    assert "later positive grant" in " ".join(result["termination_reasons"])
    assert rows[-1]["closing_cash"] == 94980
