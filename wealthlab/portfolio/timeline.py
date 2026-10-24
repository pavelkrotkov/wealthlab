"""Entitlements precede receipts, fees and trades; policies cannot observe future events."""

from wealthlab.portfolio.distributions import entitle, pay, recognize
from wealthlab.portfolio.fees import assess_date
from wealthlab.portfolio.harvesting import execute as harvest
from wealthlab.portfolio.policy_execution import execute


def distribution_events(case):
    events = []
    for index, item in enumerate(case.distributions):
        dates = (item.ex_date, item.recognition_date, item.payment_date)
        events.extend(
            (when, kind, index, item) for kind, when in enumerate(dates) if when <= case.end
        )
    return events


def events(case):
    dates = {period.date for schedule in case.fee_schedules for period in schedule.periods}
    result = distribution_events(case) + [(when, 3, 0, when) for when in dates]
    for kind, items in enumerate((case.trades, case.sale_policies, case.harvest_policies), 4):
        result.extend((item.date, kind, index, item) for index, item in enumerate(items))
    return sorted(result, key=lambda item: item[:3])


def handlers(case, book, decisions):
    return {
        0: lambda event: entitle(book, event),
        1: lambda event: recognize(book, event),
        2: lambda event: pay(book, event),
        3: lambda event: assess_date(case, book, event),
        4: book.trade,
        5: lambda event: decisions.append(execute(case, book, event)),
        6: lambda event: book.harvest_decisions.extend(harvest(book, event)),
    }


def replay(case, book):
    decisions = []
    actions = handlers(case, book, decisions)
    for _, kind, _, event in events(case):
        actions[kind](event)
    return decisions
