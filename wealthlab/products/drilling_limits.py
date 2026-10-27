"""Apply separate supplied limitation amounts without inferring eligibility or jurisdiction law."""


def limited(ledger, item, jurisdiction, eligible):
    caps = getattr(item, jurisdiction + "_limits")
    risk = ledger.bases["at_risk"] if jurisdiction == "federal" else caps.at_risk
    amount = min(eligible, *caps.model_dump().values(), ledger.bases[jurisdiction], risk)
    choice = getattr(item, jurisdiction + "_timing")
    validate_effects(item, jurisdiction, choice, amount)
    audit = dict(
        id=item.id,
        component=item.component,
        jurisdiction=jurisdiction,
        requested=getattr(item, jurisdiction + "_requested"),
        funded_eligible=eligible,
        limited_amount=amount,
        treatment=choice.treatment,
        release_on=choice.release_on,
        supplied_limits=caps.model_dump(mode="json"),
    )
    return amount, choice, audit


def validate_effects(item, jurisdiction, choice, amount):
    if choice.treatment == "denied":
        return
    if amount > getattr(item, jurisdiction + "_basis_reduction"):
        raise ValueError("A supplied drilling deduction needs its corresponding basis reduction.")
    if jurisdiction == "federal" and amount > item.at_risk_reduction:
        raise ValueError("A supplied drilling deduction needs its corresponding at-risk reduction.")
