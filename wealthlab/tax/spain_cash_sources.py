"""Explicit ordinary USD bank-cash links use actual December closing balances.

Only the native cash value changes. Fiscal ownership, inclusion and the dated
EUR quote remain independently supplied; no wealth-tax formula is duplicated.
"""

from datetime import date

from wealthlab.tax.spain_execution_facts import SpainExecution


def validate(scenario, spain, bindings):
    if spain is None:
        if bindings:
            raise ValueError("Spanish cash bindings require the native Spain context.")
        return
    pairs = unique_links(bindings)
    if pairs != expected(scenario, spain):
        raise ValueError("Every projected Spanish-year USD cash account needs a fiscal cash link.")
    for binding in bindings:
        validate_binding(scenario, spain, binding)
    validate_shares(scenario, spain, bindings)


def expected(scenario, spain):
    return {
        (annual.id, account.id)
        for annual in spain.assessments.annuals
        for account in scenario.accounts
        if account.wrapper == "cash"
        and account.owner in {annual.case.person_id, "joint"}
        and scenario.start <= date(annual.case.year, 12, 31) < scenario.end
    }


def records(scenario, spain, binding):
    try:
        annual = {a.id: a.case for a in spain.assessments.annuals}[binding.annual_id]
        account = {a.id: a for a in scenario.accounts}[binding.account_id]
        asset = {a.id: a for a in annual.assets}[binding.asset_id]
    except KeyError:
        raise ValueError(
            "A fiscal cash link must name existing annual/account/asset records."
        ) from None
    return annual, account, asset


def validate_binding(scenario, spain, binding):
    annual, account, asset = records(scenario, spain, binding)
    actual = (
        account.wrapper,
        account.currency,
        asset.kind,
        asset.product,
        asset.treatment,
        asset.fiscal_value.currency,
    )
    expected = ("cash", "USD", "financial", "ordinary", "included", "USD")
    if actual != expected or account.owner not in {annual.person_id, "joint"}:
        raise ValueError(
            "Fiscal cash links retain ordinary USD cash, person and year-end FX facts."
        )
    if account.owner != "joint" and asset.ownership_share != 1:
        raise ValueError("A solely owned native cash account retains full fiscal ownership.")


def rebind(scenario, spain, bindings, rows):
    if not bindings:
        return spain
    validate(scenario, spain, bindings)
    data = spain.model_dump(mode="json")
    for binding in bindings:
        original, _, _ = records(scenario, spain, binding)
        values = closing_balances(rows, original.year)
        annual = next(
            a["case"] for a in data["assessments"]["annuals"] if a["id"] == binding.annual_id
        )
        asset = next(a for a in annual["assets"] if a["id"] == binding.asset_id)
        asset["fiscal_value"]["amount"] = str(values[binding.account_id])
    return SpainExecution.model_validate(data)


def closing_balances(rows, year):
    found = [r for r in rows if r["period_end"] == f"{year + 1}-01-01"]
    if len(found) != 1:
        raise ValueError("A fiscal cash link requires its actual December closing balance.")
    return found[0]["account_balances"]


def unique_links(bindings):
    pairs = {(b.annual_id, b.account_id) for b in bindings}
    assets = {(b.annual_id, b.asset_id) for b in bindings}
    if len(pairs) != len(bindings) or len(assets) != len(bindings):
        raise ValueError("Bind each Spanish annual cash account and fiscal asset exactly once.")
    return pairs


def validate_shares(scenario, spain, bindings):
    shares = {}
    for binding in bindings:
        annual, _, asset = records(scenario, spain, binding)
        key = (binding.account_id, annual.year)
        shares[key] = shares.get(key, 0) + asset.ownership_share
    if any(value > 1 for value in shares.values()):
        raise ValueError("Fiscal ownership cannot count the same native cash account twice.")
