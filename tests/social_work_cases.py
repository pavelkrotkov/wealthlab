"""Synthetic helpers keep independently calculated work-test cases small."""

from datetime import date

from wealthlab.retirement.social_work import run
from wealthlab.retirement.social_work_case import SocialWorkCase
from wealthlab.retirement.social_work_example import synthetic


def payload():
    return synthetic().model_dump(mode="json")


def calculate(data):
    return run(SocialWorkCase.model_validate(data))


def cash(result, year, month):
    return next(r for r in result["monthly_cash"] if r["payment_month"] == date(year, month, 1))


def work(result, year):
    return next(r for r in result["annual_work_assessments"] if r["year"] == year)
