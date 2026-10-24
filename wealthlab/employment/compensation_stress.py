"""A dated joint job/asset shock is an explicit what-if, not an inferred probability."""

from datetime import date
from decimal import Decimal

from wealthlab.employment.compensation_events import Forfeit, NetReturn
from wealthlab.employment.compensation_example import synthetic
from wealthlab.employment.inputs import WageChange


def linked_shock(case=None, when=date(2026, 10, 1), decline=Decimal("-.5")):
    case = synthetic() if case is None else case
    path = case.employment_plan.paths[0]
    worker = next(m for m in case.members if m.id == path.owner)
    if when >= worker.retirement_date:
        raise ValueError("A linked job-loss shock must precede the member's retirement cutoff.")
    job = WageChange(
        id="shock_job_loss", provenance="assumption", date=when, kind="job_loss", multiplier=0
    )
    changed = path.model_copy(
        update=dict(changes=[e for e in path.changes if e.date < when] + [job])
    )
    employment = case.employment_plan.model_copy(update=dict(paths=[changed]))
    tranche = case.compensation_plan.tranches[0]
    market = NetReturn(
        id="shock_return",
        provenance="assumption",
        date=when,
        sequence=1,
        tranche=tranche.id,
        kind="net_return",
        rate=decline,
    )
    lost = Forfeit(
        id="shock_forfeit",
        provenance="assumption",
        date=when,
        sequence=2,
        tranche=tranche.id,
        kind="forfeit",
        amount=None,
    )
    plan = case.compensation_plan.model_copy(
        update=dict(events=[*case.compensation_plan.events, market, lost])
    )
    return case.model_copy(
        update=dict(
            name="Synthetic linked job loss, employer loss and forfeiture",
            employment_plan=employment,
            compensation_plan=plan,
        )
    )
