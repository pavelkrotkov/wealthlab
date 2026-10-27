"""Editable country context keeps each native assessment beside its shared cash scenario."""

from wealthlab.household.scenario import Scenario
from wealthlab.tax.facts import TaxModel
from wealthlab.tax.spain_execution_facts import SpainExecution


class JurisdictionExecutionCase(TaxModel):
    scenario: Scenario
    spain: SpainExecution | None = None
