"""Unpaid net medical liabilities stay distinct from paid reimbursement receipts.

Bills are supplied after insurance/other reimbursement. A direct HSA election
is an upper bound, not proof of medical eligibility or available assets. Cash
pays a remaining bill in the household healthcare slot; only actual paid,
undeducted amounts can become a later reimbursement receipt.
"""

from datetime import date
from decimal import Decimal
from typing import Literal, Self

from pydantic import Field, model_validator

from wealthlab.household.records import Identifier, Money, Record
from wealthlab.retirement.hsa_inputs import MedicalReceipt


class MedicalBill(Record):
    incurred: date
    date: date
    amount: Money = Field(gt=0)
    eligible_owners: list[Identifier] = Field(min_length=1, max_length=2)
    eligibility: Literal["qualified_medical", "not_qualified", "unresolved"]
    hsa_source: Identifier | None = None
    hsa_amount: Money = Decimal(0)
    hsa_mode: Literal["qualified_only", "allow_nonqualified"] = "qualified_only"

    @model_validator(mode="after")
    def payment_scope(self) -> Self:
        if self.incurred > self.date:
            raise ValueError("Medical bills cannot be due before the supplied care date.")
        if self.hsa_amount > self.amount:
            raise ValueError("A bill's direct HSA election cannot exceed the net liability.")
        if self.hsa_amount and self.hsa_source is None:
            raise ValueError("A positive direct medical HSA election needs a source account.")
        return self

    def receipt(self):
        """Metadata only: the dynamic book starts its available paid balance at zero."""
        return MedicalReceipt(
            id=self.id,
            provenance=self.provenance,
            eligible_owners=self.eligible_owners,
            incurred=self.incurred,
            paid=self.date,
            amount=self.amount,
            reimbursed_elsewhere=0,
            deducted_federally=0,
            eligibility=self.eligibility,
        )
