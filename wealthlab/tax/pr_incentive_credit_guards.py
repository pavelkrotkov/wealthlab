"""Unsupported NIIT/special-tax credit classifications withhold the affected aggregate."""


def credit(slices, us):
    if us["income_tax"] <= 0:
        return
    eligible = [item for item in slices if item.treatment in {"ordinary", "lt15"}]
    regular_credit_guards(eligible, us)
    # Act60's in-lieu tax arises under special law; the Code's general paid-tax
    # credit language alone does not prove its application to these buckets.
    uncertain = [item for item in slices if item.treatment in {"special4", "special5"}]
    if has_foreign_income(uncertain):
        raise ValueError(
            "Act60 4%/5% US-source foreign-credit treatment is unsupported; aggregate withheld."
        )


def regular_credit_guards(eligible, us):
    foreign = has_foreign_income(eligible)
    if not foreign:
        return
    # US FTC cannot offset NIIT. Whether PR credits the NIIT itself is a
    # different question, so a missing primary answer cannot become a zero.
    if us["niit"]:
        raise ValueError(
            "PR credit eligibility for US NIIT needs verified treatment; aggregate withheld."
        )
    # Basis/source and preferential-deduction differences need their own
    # Schedule C paid-tax reduction; a gross-income ratio would conceal them.
    if any(item.row.federal_amount != item.row.pr_amount for item in eligible):
        raise ValueError("PR paid-tax reduction with different recognized bases is unsupported.")
    treatments = {item.treatment for item in eligible if item.row.pr_amount}
    if {"ordinary", "lt15"}.issubset(treatments):
        raise ValueError(
            "Mixed ordinary/preferential source-credit allocation needs a separate profile."
        )


def has_foreign_income(slices):
    return any(item.row.pr_source == "US" and item.row.pr_amount for item in slices)
