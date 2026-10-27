"""Source-backed employment applicability does not infer a contract from ownership."""

from datetime import date

from pydantic import Field

from wealthlab.employment.compensation_inputs import CompensationPlan
from wealthlab.employment.inputs import EmploymentPlan
from wealthlab.household.records import Identifier, Record


class EmploymentSource(Record):
    source: str = Field(min_length=10, max_length=1000)
    source_date: date
    available_on: date
    all_candidate_income_and_market_paths_confirmed: bool = False
    complete_cash_tax_vesting_forfeiture_and_exit_facts_confirmed: bool = False


class EmployerIndependence(EmploymentSource):
    """The whole supplied compensation plan is unaffected by all candidate work choices."""

    tranche_ids: list[Identifier] = Field(min_length=1)
    independent_of_all_candidate_employment_and_retirement_confirmed: bool = False


class EmploymentOffer(EmploymentSource):
    """One complete native event profile for exactly one all-member retirement-date map."""

    retirement_dates: dict[Identifier, date]
    employment_plan: EmploymentPlan | None
    compensation_plan: CompensationPlan
