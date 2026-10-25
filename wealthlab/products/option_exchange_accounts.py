"""Competing product books cannot duplicate capital or contradict their no-wash profiles."""


def validate(scenario):
    option, exchange = scenario.option_plan, scenario.exchange_fund_plan
    if option is None or exchange is None:
        return
    if option.account_id == exchange.account_id:
        raise ValueError("Options and exchange funds cannot share the same household account.")
    groups = {security.wash_group for security in option.case.holdings.securities}
    exchange_groups = {
        exchange.source_security.wash_group,
        *(item.security.wash_group for item in exchange.basket),
    }
    if groups & exchange_groups:
        raise ValueError("Options and exchange funds cannot share a known wash group.")
