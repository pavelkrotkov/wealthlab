"""Actual settlement debt accrues the explicitly supplied simple ACT/365 financing rate."""

from decimal import Decimal

from wealthlab.household.calendar import money


def accrue(state, previous, day):
    cost = money(
        state.loan
        * Decimal(str(state.case.settlement_loan_annual_rate))
        * Decimal((day - previous).days)
        / 365
    )
    if cost:
        state.cash(-cost, "settlement_loan_interest", day)
