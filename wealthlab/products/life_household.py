"""Persistent policy books share the household wallet and recognized annual return."""

from wealthlab.products.life_contract_book import PolicyBook
from wealthlab.products.life_household_cash import execute
from wealthlab.products.life_household_reporting import summarize
from wealthlab.products.life_household_validation import validate
from wealthlab.products.life_household_values import mark


class Ledger:
    def __init__(self, scenario, tax):
        validate(scenario)
        if tax is None:
            raise ValueError("Policy execution requires the active household tax ledger.")
        self.scenario, self.plan, self.tax = scenario, scenario.life_plan, tax
        self.books = {
            h.account_id: PolicyBook(h.contract.opening_federal_basis, h.contract.opening_loan)
            for h in self.plan.holdings
        }
        self.owners = {a.id: a.owner for a in scenario.accounts}
        self.log, self.cancelled, self.values = [], [], []
        self.summary = {}

    def after_receipts(self, wallet, start, end):
        rows = []
        for _, _, _, holding, event in scheduled(self.plan, start, end):
            if self.books[holding.account_id].closed:
                self.cancelled.append(
                    dict(
                        account_id=holding.account_id,
                        event=event.id,
                        reason="policy already terminated",
                    )
                )
                continue
            row, recognized = execute(self, holding, event, wallet, start, end)
            rows.append(row)
            self.log.append(row)
            yield recognized
        values = [mark(self, holding, wallet, end) for holding in self.plan.holdings]
        self.values.append(dict(date=end.isoformat(), policies=values))
        self.summary = summarize(self, rows, values, end)

    def finish(self, rows):
        rows[-1]["life_policy_audit"] = dict(
            inputs=self.plan.model_dump(mode="json"),
            executed=self.log,
            cancelled=self.cancelled,
            values=self.values,
        )


def scheduled(plan, start, end):
    return sorted(
        (event.date, i, j, holding, event)
        for i, holding in enumerate(plan.holdings)
        for j, event in enumerate(holding.contract.events)
        if start <= event.date < end
    )
