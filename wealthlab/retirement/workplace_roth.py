"""Actual funded payroll adds cost; Roth plan cash consumes the complete contract pool.

Cash recovery cannot exceed paid principal or cost, even after a loss. Residual
unrecovered cost in an empty separated contract is reported, with no inferred
loss deduction and no reopening via later employee deferrals in this profile.
"""

from decimal import Decimal

from wealthlab.household.calendar import money
from wealthlab.retirement.roth_reconciliation import half_birthday

ZERO = Decimal(0)


class Ledger:
    def __init__(self, scenario):
        self.config = scenario.workplace_plan.roth_cash_withdrawals
        self.source_contract = {
            source: key for key, c in self.config.contracts.items() for source in c.sources
        }
        self.basis = {
            key: dict(federal=c.federal_basis, nj=c.nj_basis)
            for key, c in self.config.contracts.items()
        }
        self.first = {
            key: c.first_federal_contribution_year for key, c in self.config.contracts.items()
        }
        self.audit = []

    def contribute(self, order, funded):
        if order.kind != "roth_401k" or not funded:
            return
        key = self.source_contract[order.destination]
        for jurisdiction in self.basis[key]:
            self.basis[key][jurisdiction] += funded
        if self.first[key] is None:
            self.first[key] = order.date.year

    def distribute(self, source, gross, wallet, when, born):
        key = self.source_contract[source]
        contract = self.config.contracts[key]
        value = sum((wallet.balances[s] for s in contract.sources), ZERO)
        first = self.first[key]
        qualified = first is not None and when.year - first >= 5 and when >= half_birthday(born)
        result = dict(contract=key, contract_value_before=value, federal_qualified=qualified)
        for jurisdiction, basis in self.basis[key].items():
            recovered = recovery(basis, value, gross)
            self.basis[key][jurisdiction] -= recovered
            result[f"{jurisdiction}_basis_recovered"] = recovered
            result[f"{jurisdiction}_taxable"] = ZERO if qualified else gross - recovered
            result[f"{jurisdiction}_basis_remaining"] = self.basis[key][jurisdiction]
        result.update(nj_treatment=contract.nj_treatment, first_federal_contribution_year=first)
        return result

    def snapshot(self, wallet):
        return [
            dict(
                contract=key,
                sources=list(contract.sources),
                value=sum((wallet.balances[source] for source in contract.sources), ZERO),
                federal_basis=self.basis[key]["federal"],
                nj_basis=self.basis[key]["nj"],
                first_federal_contribution_year=self.first[key],
                nj_treatment=contract.nj_treatment,
                modeled_cash_loss_deduction=ZERO,
            )
            for key, contract in self.config.contracts.items()
        ]


def recovery(basis, value, gross):
    if not value:
        return ZERO
    return min(basis, gross, money(gross * min(Decimal(1), basis / value)))


def make(scenario):
    return Ledger(scenario) if scenario.workplace_plan.roth_cash_withdrawals is not None else None


def contribute(ledger, order, funded):
    if ledger is not None:
        ledger.contribute(order, funded)


def snapshot(ledger, wallet):
    return dict(workplace_roth_contracts=ledger.snapshot(wallet)) if ledger is not None else {}
