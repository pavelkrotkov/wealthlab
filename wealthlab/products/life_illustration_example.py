"""Invented small-dollar illustration paths; no insurer or policy is represented."""

from wealthlab.products.life_illustration_inputs import LifeStudy


def synthetic():
    cases = [case(scale) for scale in ("guaranteed", "current", "stressed")]
    long = case("current")
    long.update(
        id="long_duration",
        name="Long-duration supplied path",
        premium_pattern="long_duration",
        stop_funding_date=None,
        funding_path="Three supplied annual premiums",
    )
    long["flows"].append(flow("third_premium", "2028-01-01", "1000"))
    long["values"][-1].update(gross_cash_value="3100", gross_surrender_value="3000")
    stop = case("current")
    stop.update(
        id="stop_funding", name="Stop-funding values unavailable", stop_funding_date="2026-01-01"
    )
    stop["flows"] = stop["flows"][:1]
    stop["values"] = [
        dict(
            date="2029-01-01",
            gross_cash_value=None,
            gross_surrender_value=None,
            gross_death_benefit=None,
        )
    ]
    return LifeStudy.model_validate(
        dict(
            synthetic=True,
            retirement_date="2027-01-01",
            insurance_need="6000",
            illustrations=[*cases, long, stop],
        )
    )


def case(scale):
    cash = {
        "guaranteed": ("750", "1650", "1900"),
        "current": ("900", "1950", "2250"),
        "stressed": ("800", "1750", "2000"),
    }[scale]
    return dict(
        id=scale,
        provenance="illustration",
        name=f"Limited-pay {scale} path",
        scale=scale,
        source="Invented teaching illustration, not policy terms or insurer performance",
        source_date="2026-01-01",
        issue_date="2026-01-01",
        premium_pattern="limited_pay",
        funding_path="Two dated premiums; values supplied independently",
        stop_funding_date="2027-01-01",
        complete_history_from_issue_confirmed=True,
        values_match_cashflows_and_funding_path_confirmed=True,
        flows=[
            flow("first_premium", "2026-01-01", "1000"),
            flow("second_premium", "2027-01-01", "1000"),
        ],
        values=[
            dict(
                date=f"{2027 + i}-01-01",
                gross_cash_value=value,
                gross_surrender_value=str(int(value) - 100),
                gross_death_benefit="5000",
            )
            for i, value in enumerate(cash)
        ],
    )


def flow(identifier, when, amount, kind="premium"):
    return dict(id=identifier, provenance="illustration", date=when, kind=kind, amount=amount)
