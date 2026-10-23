"""Replay dated information: fee assessments, manual trades, sale policies, then harvests."""

from wealthlab.portfolio.fees import assess_date
from wealthlab.portfolio.harvesting import execute as harvest
from wealthlab.portfolio.policy_execution import execute


def events(case):
    dates = {period.date for schedule in case.fee_schedules for period in schedule.periods}
    events = [(when, 0, 0, when) for when in dates]
    events += [(item.date, 1, index, item) for index, item in enumerate(case.trades)]
    events += [(item.date, 2, index, item) for index, item in enumerate(case.sale_policies)]
    events += [(item.date, 3, index, item) for index, item in enumerate(case.harvest_policies)]
    return sorted(events, key=lambda item: item[:3])


def replay(case, book):
    decisions = []
    for _, kind, _, event in events(case):
        if kind == 0:
            assess_date(case, book, event)
        elif kind == 1:
            book.trade(event)
        elif kind == 2:
            decisions.append(execute(case, book, event))
        else:
            book.harvest_decisions.extend(harvest(book, event))
    return decisions
