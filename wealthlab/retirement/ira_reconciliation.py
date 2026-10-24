"""Annual actual basis recovery; these results never feed earlier funding decisions."""

from decimal import Decimal

from wealthlab.household.calendar import money


def recovered(rows, basis, ending, key):
    """Cumulative cent allocation preserves the total and prevents double recovery.

    The common fraction uses year-end IRA value plus all distributed/converted
    amounts. Basis can exceed value after losses, but recovery cannot exceed
    either the withdrawn principal or unrecovered basis.
    """
    gross = sum((row["paid"] for row in rows), Decimal(0))
    denominator = ending + gross
    ratio = min(Decimal(1), basis / denominator) if denominator else Decimal(0)
    running, allocated = Decimal(0), Decimal(0)
    for row in rows:
        running += row["paid"]
        target = min(basis, money(running * ratio))
        row[key] = target - allocated
        allocated = target
    return basis - allocated


def traditional(case, book, person):
    rows = [r for r in book["rows"] if r["owner"] == person.id and r["wrapper"] == "traditional"]
    ending = value(book, person.id, "traditional")
    fed = recovered(rows, person.federal_ira_basis, ending, "federal_basis_recovered")
    nj = recovered(rows, person.nj_ira_basis, ending, "nj_basis_recovered")
    for row in rows:
        row["federal_taxable"] = row["paid"] - row["federal_basis_recovered"]
        row["nj_taxable"] = row["paid"] - row["nj_basis_recovered"]
    return dict(federal_ira_basis=fed, nj_ira_basis=nj)


def value(book, owner, wrapper):
    return sum(
        (
            book["balances"][account.id]
            for account in book["accounts"].values()
            if account.owner == owner and account.wrapper == wrapper
        ),
        Decimal(0),
    )
