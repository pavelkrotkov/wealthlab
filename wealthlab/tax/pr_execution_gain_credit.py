"""Prove the bounded mixed-credit case without allocating US preferential tax by gross income.

Schedule C Part III reduces paid US income tax only for income taxed in the
US but excluded locally. When all US-taxable receipts survive locally in
regular/15% buckets at the same recognized basis, that reduction is zero.
PR-source salary can be excluded under section933 without changing this
proof: it contributes neither US liability nor paid US tax. The existing
native PR limitation still applies separately to the actual local net base.
"""

from wealthlab.tax.pr_incentive_credit_guards import has_foreign_income


def complete_mixed(taxable, slices, us):
    eligible = [s for s in slices if s.treatment in {"ordinary", "lt15"}]
    if not mixed(eligible) or not has_foreign_income(eligible):
        return False
    if us["niit"] or different_basis(eligible):
        return False
    return covers(taxable, eligible)


def mixed(slices):
    treatments = {s.treatment for s in slices if s.row.pr_amount}
    return {"ordinary", "lt15"}.issubset(treatments)


def different_basis(slices):
    return any(s.row.federal_amount != s.row.pr_amount for s in slices)


def covers(taxable, slices):
    rows = [s.row for s in slices]
    return all(row in rows for row in taxable)
