"""Federal receipt matching and supplied NJ gross-withdrawal fractions remain independent."""

from hsa_distribution_cases import change, flat

from wealthlab.household.projection import project


def test_partial_qualified_receipt_does_not_hide_the_unqualified_remainder():
    def configure(data):
        plan = data["hsa_plan"]
        plan["medical_receipts"] = [
            dict(
                id="paid",
                provenance="assumption",
                eligible_owners=["person_a"],
                incurred="2025-05-01",
                paid="2025-06-01",
                amount="2000",
                reimbursed_elsewhere="0",
                deducted_federally="0",
                eligibility="qualified_medical",
            )
        ]
        plan["withdrawals"][0]["receipt_ids"] = ["paid"]

    rows = project(change(flat(nj_fraction="0.5"), configure))
    final = rows[-1]
    assert (
        sum(r["hsa_qualified_reimbursements"] for r in rows),
        sum(r["hsa_nonqualified_taxable"] for r in rows),
    ) == (2000, 3000)
    assert sum(r["hsa_nj_withdrawal_income"] for r in rows) == 2500
    assert final["hsa_audit"]["receipt_remaining"]["paid"] == 0
    assert final["net_wealth"] == 109400
    assert final["annual_tax"]["new_jersey"]["gross_income"] == 2500
