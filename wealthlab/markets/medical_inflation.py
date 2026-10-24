"""Index dated medical costs using only CPI observed before their due month.

The existing bill ledger still decides actual provider/cash payments and
unpaid liabilities. Indexed forecasts never create paid receipt capacity.
The original household and binding stay in the reproduction export.
"""

from decimal import Decimal
from typing import Literal

from wealthlab.household.calendar import money, months
from wealthlab.household.records import Identifier
from wealthlab.tax.facts import TaxModel


class MedicalBillIndexing(TaxModel):
    bill_id: Identifier
    amount_basis: Literal["projection_start_prices"]
    hsa_election: Literal["keep_nominal_cap", "keep_bill_share"] = "keep_nominal_cap"


def validate(scenario, binding):
    selected = [b.bill_id for b in binding.medical_bill_inflation]
    if not selected:
        return
    if scenario.hsa_plan is None:
        raise ValueError("Medical bill inflation needs an explicit household HSA/bill plan.")
    bills = {b.id: b for b in scenario.hsa_plan.medical_bills}
    if len(selected) != len(set(selected)) or not set(selected) <= bills.keys():
        raise ValueError("Medical bill inflation IDs must be unique existing bills.")
    validate_dates(scenario, bills, selected)


def validate_dates(scenario, bills, selected):
    if any(not scenario.start <= bills[key].date < scenario.end for key in selected):
        raise ValueError("Indexed medical bills must fall inside the realized market horizon.")


def compile_bills(payload, scenario, batch, binding, index):
    if not binding.medical_bill_inflation:
        return
    prices = price_levels(scenario, batch, index)
    targets = {b.bill_id: b for b in binding.medical_bill_inflation}
    originals = {b.id: b for b in scenario.hsa_plan.medical_bills}
    for value in payload["hsa_plan"]["medical_bills"]:
        if value["id"] not in targets:
            continue
        original = originals[value["id"]]
        factor = prices[(original.date.year, original.date.month)]
        amount = money(original.amount * factor)
        if amount <= 0:
            raise ValueError(
                "Indexed medical costs round to zero; this profile needs positive cents."
            )
        cap = original.hsa_amount
        if targets[original.id].hsa_election == "keep_bill_share":
            cap = money(cap * factor)
        value.update(amount=str(amount), hsa_amount=str(min(cap, amount)))


def price_levels(scenario, batch, index):
    prices, current = {}, Decimal(1)
    for n, (start, _) in enumerate(months(scenario.start, scenario.end)):
        prices[(start.year, start.month)] = current
        current *= Decimal(str(1 + batch.inflation[index, n]))
    return prices


def audit(original, compiled, binding):
    if not binding.medical_bill_inflation:
        return []
    before = {b.id: b for b in original.hsa_plan.medical_bills}
    after = {b.id: b for b in compiled.hsa_plan.medical_bills}
    return [
        dict(
            bill=b.bill_id,
            date=after[b.bill_id].date,
            input_amount=before[b.bill_id].amount,
            realized_amount=after[b.bill_id].amount,
            hsa_election=b.hsa_election,
            amount_basis=b.amount_basis,
            input_hsa_cap=before[b.bill_id].hsa_amount,
            realized_hsa_cap=after[b.bill_id].hsa_amount,
        )
        for b in binding.medical_bill_inflation
    ]
