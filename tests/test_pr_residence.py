"""Independent statutory move-year boundary conditions and local recognition dates."""

from datetime import date

import pytest

from wealthlab.tax.pr_examples import synthetic
from wealthlab.tax.pr_facts import Residence, SourceIncome
from wealthlab.tax.pr_recognition import recognized
from wealthlab.tax.pr_residence import excluded, federal_status, local_period


def residence(**changes):
    data = synthetic().primary.model_dump()
    data.update(changes)
    return Residence.model_validate(data)


@pytest.mark.parametrize("days,eligible", [(182, None), (183, True)])
def test_presence_183_boundary(days, eligible):
    assert federal_status(residence(presence_days=days), 2025)["eligible"] == eligible


def test_move_in_requires_last_183_days_and_prior_and_future_history():
    # July 2 through Dec 31 is 183 days. Future residence is an explicit condition,
    # so an assumed future history cannot become an unconditional qualification.
    claims = dict(
        federal_bfr="move_in",
        local_start=date(2025, 7, 2),
        prior_three_nonresident="confirmed",
        next_three_resident="assumed",
    )
    result = federal_status(residence(**claims), 2025)
    assert result["eligible"] is True
    assert result["conditional"]
    claims["local_start"] = date(2025, 7, 3)
    assert federal_status(residence(**claims), 2025)["eligible"] is None
    claims.update(local_start=date(2025, 7, 2), next_three_resident="unset")
    assert federal_status(residence(**claims), 2025)["eligible"] is None


def test_departure_exception_requires_prior_two_years_and_stops_exclusion():
    # Citizenship plus prior two-year residence supports the departure exception.
    # The first post-departure receipt remains taxable federally.
    person = residence(
        federal_bfr="move_out", local_end=date(2025, 6, 30), prior_two_resident="confirmed"
    )
    status = federal_status(person, 2025)
    row = synthetic().income[0].model_copy(update={"received": date(2025, 6, 30)})
    assert excluded(row, person, status, 2025)
    assert not excluded(row.model_copy(update={"received": date(2025, 7, 1)}), person, status, 2025)
    assert (
        federal_status(residence(federal_bfr="move_out", local_end=None), 2025)["eligible"] is None
    )


def test_local_move_year_worldwide_period_and_pr_source_outside_it():
    # Hacienda includes worldwide income while resident and PR-source income
    # outside that period; federal BFR labels do not determine this local period.
    case = synthetic()
    person = residence(local_start=date(2025, 7, 1))
    row = case.income[0]
    before = row.model_copy(update={"received": date(2025, 6, 30), "pr_source": "US"})
    after = before.model_copy(update={"received": date(2025, 7, 1)})
    pr_before = before.model_copy(update={"pr_source": "PR"})
    assert recognized(
        case.model_copy(update={"primary": person, "income": [before, after, pr_before]})
    ) == [after, pr_before]
    assert local_period(Residence(), 2025) is None
    with pytest.raises(ValueError, match="period"):
        recognized(case.model_copy(update={"primary": Residence()}))


def test_invalid_source_components_and_residence_order():
    with pytest.raises(ValueError, match="start"):
        residence(local_start=date(2026, 1, 1))
    values = synthetic().income[0].model_dump()
    with pytest.raises(ValueError, match="dividends"):
        SourceIncome.model_validate(dict(values, qualified_dividends=1))
    with pytest.raises(ValueError, match="wage"):
        SourceIncome.model_validate(dict(values, kind="interest", us_government_wages=True))
