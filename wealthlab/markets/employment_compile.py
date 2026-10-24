"""A first observed drawdown may cause next-month job loss and supplied forfeiture.

This conditional trigger is not a calibrated employment-risk model. A return to
work uses the specified baseline-pay multiplier after a fixed number of months;
future manual changes are replaced only after explicit confirmation. Retirement
cutoffs still stop wages. No generated wages depend on future observations.
"""

from decimal import Decimal

from wealthlab.household.calendar import months
from wealthlab.markets.employer_links import active
from wealthlab.markets.wrapper_compile import event_id


def trigger(scenario, batch, item, index):
    link = item.employment
    path = next(p for p in scenario.employment_plan.paths if p.id == link.path_id)
    owner = next(m for m in scenario.members if m.id == path.owner)
    factor = batch.assets.index(item.factor)
    value = peak = Decimal(1)
    for month, (_, end) in enumerate(months(scenario.start, scenario.end)):
        value *= 1 + Decimal(str(batch.mark_returns[index, month, factor]))
        peak = max(peak, value)
        if eligible(scenario, path, owner, end) and 1 - value / peak >= link.drawdown_trigger:
            return end
    return None


def compile_link(payload, scenario, batch, item, index, tranches):
    when = trigger(scenario, batch, item, index)
    if when is None:
        return
    replace_work(payload, scenario, item.employment, when)
    if item.employment.forfeit_remaining_unvested:
        append_forfeitures(payload, item, tranches, when)


def replace_work(payload, scenario, link, when):
    paths = payload["employment_plan"]["paths"]
    path = next(p for p in paths if p["id"] == link.path_id)
    path["changes"] = [e for e in path["changes"] if e["date"] < str(when)]
    path["changes"].append(
        dict(
            id=event_id(link.path_id, when, "job_loss"),
            provenance="assumption",
            date=when,
            kind="job_loss",
            multiplier=0,
        )
    )
    resume = add_months(when, link.months_out)
    owner = next(m for m in scenario.members if m.id == path["owner"])
    if resume < min(scenario.end, owner.retirement_date):
        path["changes"].append(
            dict(
                id=event_id(link.path_id, resume, "return_to_work"),
                provenance="assumption",
                date=resume,
                kind="return_to_work",
                multiplier=link.return_multiplier,
            )
        )


def append_forfeitures(payload, item, tranches, when):
    for offset, tranche in enumerate(tranches):
        payload["compensation_plan"]["events"].append(
            dict(
                id=event_id(tranche.id, when, "linked_forfeit"),
                provenance="assumption",
                date=when,
                sequence=item.event_sequence_start + offset,
                tranche=tranche.id,
                kind="forfeit",
                amount=None,
            )
        )


def add_months(when, count):
    offset = when.year * 12 + when.month - 1 + count
    return when.replace(year=offset // 12, month=offset % 12 + 1)


def eligible(scenario, path, owner, when):
    return when < min(scenario.end, owner.retirement_date) and active(path, when)


def audit(scenario, binding):
    linked = {b.employment.path_id for b in binding.employers if b.employment}
    paths = scenario.employment_plan.paths if scenario.employment_plan else []
    return [p.model_dump(mode="json") for p in paths if p.id in linked]
