"""An editable, unconfirmed starter; zero history is an assumption to replace or confirm."""


def template(scenario):
    people = [p.id for p in scenario.members]
    assumed = dict(provenance="assumption")
    used = set(people)
    case = dict(
        start_year=scenario.start.year,
        end_year=scenario.end.year,
        opening_cash=0,
        income_policy="household_completed_returns",
        complete_context=False,
        future_policy="freeze_2026",
        premium_growth=0,
        threshold_growth=0,
        payment_policy="first_of_coverage_month_fifo_arrears",
        members=[dict(id=p, **assumed) for p in people],
        coverage=[
            dict(
                id=distinct(f"coverage_{i}", used),
                member=p,
                start=scenario.start.isoformat(),
                end=scenario.end.isoformat(),
                eligibility_confirmed=False,
                part_a=True,
                part_a_monthly_2026=0,
                part_b=True,
                standard_b_premium_applicable=True,
                part_d=True,
                part_d_plan_monthly_2026=40,
                other_monthly_health_cost_2026=200,
                **assumed,
            )
            for i, p in enumerate(people)
        ],
        income_history=[
            dict(
                id=distinct(f"prior_return_{year}", used),
                year=year,
                members=people,
                filing="joint" if len(people) == 2 else "individual",
                agi=0,
                tax_exempt_interest=0,
                **assumed,
            )
            for year in [scenario.start.year - 2, scenario.start.year - 1]
        ],
    )
    return dict(
        case=case,
        collection_mode="direct_bill_only",
        ssa_current_premiums_context_confirmed=False,
        direct_billing_without_benefit_withholding_confirmed=False,
        costs_excluded_from_other_expenses_confirmed=False,
        complete_household_tax_history_confirmed=False,
    )


def distinct(candidate, used):
    while candidate in used:
        candidate = "_" + candidate
    used.add(candidate)
    return candidate
