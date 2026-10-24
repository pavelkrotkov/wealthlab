"""Named stresses are supplied scenarios, never estimated event probabilities."""

from wealthlab.household.calendar import months

NAMES = ("early_crash", "prolonged_inflation", "concentration_loss", "illiquidity")


def events(case, name):
    count = len(list(months(case.start, case.end)))
    if name == "early_crash":
        rates = dict(equity=-0.40, bond=-0.10, employer=-0.60, cash=0, other=-0.20)
        return [dict(name=name, month=0, mark_shocks={a.id: rates[a.role] for a in case.assets})]
    if name == "prolonged_inflation":
        return [
            dict(name=name, month=i, inflation_override=1.10 ** (1 / 12) - 1)
            for i in range(min(36, count))
        ]
    if name == "concentration_loss":
        return concentration(case)
    if name == "illiquidity":
        return illiquidity(case, count)
    raise ValueError("Unknown named market stress.")


def concentration(case):
    risky = [a for a in case.assets if a.role in {"employer", "equity"}]
    if not risky:
        raise ValueError("Concentration stress needs an explicitly risky asset.")
    return [dict(name="concentration_loss", month=0, mark_shocks={risky[0].id: -0.75})]


def illiquidity(case, count):
    locks = {a.id: min(36, count) for a in case.assets if a.role != "cash"}
    if not locks:
        raise ValueError("Illiquidity stress needs a noncash asset.")
    return [dict(name="illiquidity", month=0, lock_months=locks)]
