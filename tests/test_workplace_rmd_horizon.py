"""Public workplace projections require full years; catch-up date is not the RMD deadline.

An end date of December20 or31 is rejected before the RMD ledger can run.
For a supported December1→January1 period, the year-end target is enforced.
December1 is merely the selected automatic cash date, not an excise deadline.
"""

from datetime import date

import pytest

from wealthlab.household.funding import Wallet
from wealthlab.household.projection import project
from wealthlab.household.scenario import Scenario
from wealthlab.retirement.workplace import Ledger
from wealthlab.retirement.workplace_rmd import Ledger as RMDLedger
from wealthlab.retirement.workplace_rmd_example import synthetic
from wealthlab.retirement.workplace_rmd_reporting import month


def final_year(end, separation="2026-01-01"):
    data = synthetic().model_dump(mode="json")
    data["end"] = end
    data["tax_plan"]["cases"] = data["tax_plan"]["cases"][:1]
    data["workplace_plan"]["years"] = data["workplace_plan"]["years"][:1]
    data["workplace_plan"]["cash_withdrawals"]["profiles"]["beta"]["separation_date"] = separation
    return Scenario.model_validate(data)


@pytest.mark.parametrize("end", ["2026-12-20", "2026-12-31"])
def test_partial_final_year_is_rejected_before_any_rmd_ledger_start(end, monkeypatch):
    def forbidden(*_):
        raise AssertionError("An unsupported partial year cannot start the RMD book.")

    monkeypatch.setattr(RMDLedger, "start", forbidden)
    with pytest.raises(ValueError, match="complete calendar years"):
        project(final_year(end, "2026-12-15"))


def test_last_supported_year_does_enforce_the_source_separation_gate():
    with pytest.raises(ValueError, match="separation by December 1"):
        project(final_year("2027-01-01", "2026-12-15"))


def test_december_catchup_date_does_not_advance_the_december31_excise_deadline():
    scenario = synthetic()
    ledger = Ledger(scenario).rmd
    ledger.start(Wallet(scenario), date(2026, 1, 1))
    events, partial = month(ledger, date(2026, 12, 1), date(2026, 12, 20))
    assert not events
    assert partial["workplace_rmd_shortfall"] == 0
    assert ledger.current["beta"]["status"] == "in_year"
    events, closed = month(ledger, date(2026, 12, 1), date(2027, 1, 1))
    assert closed["workplace_rmd_shortfall"] == 20000
    assert events[0].federal.retirement_additional_tax == 5000


def test_pre_rmd_1959_horizon_does_not_validate_an_extra_unprojected_year():
    from wealthlab.retirement.workplace_example import template as workplace_context
    from wealthlab.tax.projection_example import template as tax_context

    data = synthetic().model_dump(mode="json")
    data.update(end="2032-01-01")
    data["members"][0]["birth_date"] = "1959-07-01"
    scenario = Scenario.model_validate(data)
    data["workplace_plan"]["years"] = workplace_context(scenario)["years"]
    data["tax_plan"] = tax_context(scenario).model_dump(mode="json")
    rows = project(Scenario.model_validate(data))
    assert rows[-1]["period_end"] == "2032-01-01"
    assert rows[-1]["workplace_rmd_required"] == 0
    assert rows[-1]["net_wealth"] == 492000
