"""An unconfirmed HSA starter must not invent enrollment, receipts or account history."""


def template(scenario):
    return dict(
        years=[
            dict(
                year=year,
                rule_mode="freeze_2026_assumption" if year >= 2026 else "published",
                married=len(scenario.members) == 2,
                owners=[
                    dict(
                        id=p.id,
                        provenance="assumption",
                        birth_date=p.birth_date.isoformat(),
                        established=None,
                        months=[
                            dict(
                                month=month,
                                coverage="none",
                                disqualifying_coverage=False,
                                medicare=False,
                                claimable_dependent=False,
                            )
                            for month in range(1, 13)
                        ],
                    )
                    for p in scenario.members
                ],
            )
            for year in range(scenario.start.year, scenario.end.year)
        ],
        medical_receipts=[],
        contributions=[],
        withdrawals=[],
        interest=[],
        nj_treatment="taxable_bank_interest_assumption",
        conditional_nj_treatment_confirmed=False,
        cash_only_accounts_and_complete_context_confirmed=False,
        receipts_paid_before_projection_confirmed=False,
        employer_funding_excluded_from_other_nj_wages_confirmed=False,
        priority="after_receipts_before_ira_and_current_tax",
    )
